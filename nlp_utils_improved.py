"""
nlp_utils_improved.py
Improved NLP utilities with robust line-based extraction for quantity, timing, and duration.
"""

import re
import difflib
from typing import Dict, List, Optional


MEDICINE_LIST = [
    "augmentin", "enzoflam", "pantoprazole", "hexigel", "paracetamol",
    "amoxicillin", "metformin", "atorvastatin", "omeprazole", "cetirizine",
    "azithromycin", "ibuprofen", "aspirin", "metronidazole", "ciprofloxacin",
    "diclofenac", "ranitidine", "losartan", "amlodipine", "hydrochlorothiazide",
    "prednisone", "warfarin", "insulin", "levothyroxine", "simvastatin"
]


def extract_details_linewise(text: str, medicines: List[str]) -> List[Dict]:
    """
    Extract quantity, timing, and duration for each medicine using line-based processing.
    
    Args:
        text: Raw OCR text (may have messy spacing)
        medicines: List of detected medicine names
    
    Returns:
        List of dicts with medicine details
    """
    # Step 1: Clean text
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)  # Collapse multiple spaces
    text = text.replace(' - ', '-')   # Fix spacing around hyphens
    text = text.replace(' mg', 'mg')
    text = text.replace(' ml', 'ml')
    text = text.replace(' g ', 'g ')
    text = text.strip()
    
    print("\n" + "="*60)
    print("RAW OCR TEXT (CLEANED):")
    print(text)
    print("="*60)
    
    # Step 2: Split into lines
    lines = text.split('\n')
    results = []
    
    # Step 3: Process each line
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue
        
        # Check if this line contains a medicine
        medicine_found = None
        for med in medicines:
            if med.lower() in line:
                medicine_found = med
                break
        
        if not medicine_found:
            continue
        
        print(f"\nLINE {line_num}: {line}")
        print(f"  Medicine: {medicine_found}")
        
        # Extract quantity (mg, ml, g)
        quantity_match = re.search(r'(\d+(?:\.\d+)?)(mg|ml|g|mcg)\b', line)
        quantity = quantity_match.group(0) if quantity_match else "N/A"
        print(f"  Quantity: {quantity}")
        
        # Extract timing (1-0-1, 1-1-1, etc.)
        timing_match = re.search(r'\b([01])[-/]([01])[-/]([01])\b', line)
        if timing_match:
            timing = f"{timing_match.group(1)}-{timing_match.group(2)}-{timing_match.group(3)}"
        else:
            # Try abbreviations
            abbrev_map = {'od': '1-0-0', 'bd': '1-0-1', 'tds': '1-1-1', 'qid': '1-1-1'}
            timing = "N/A"
            for abbr, code in abbrev_map.items():
                if re.search(r'\b' + abbr + r'\b', line):
                    timing = code
                    break
        print(f"  Timing: {timing}")
        
        # Extract duration (x5 days, for 7 days, etc.)
        duration_match = re.search(r'(?:x|for|×)\s*(\d+)\s*(days?|weeks?|months?)', line)
        if not duration_match:
            duration_match = re.search(r'\b(\d+)\s*(days?|weeks?|months?)\b', line)
        duration = f"{duration_match.group(1)} {duration_match.group(2)}" if duration_match else "N/A"
        print(f"  Duration: {duration}")
        
        results.append({
            "medicine": medicine_found.capitalize(),
            "quantity": quantity,
            "when_to_take": timing,
            "duration": duration
        })
    
    print("\n" + "="*60)
    return results


def test_extraction():
    """Test the extraction function with sample prescription text."""
    test_text = """
    Tab Augmentin 625mg 1-0-1 x 5 days
    Tab Paracetamol 500mg 1-1-1 x 3 days
    """
    
    medicines = ["augmentin", "paracetamol"]
    results = extract_details_linewise(test_text, medicines)
    
    print("\nFINAL RESULTS:")
    for result in results:
        print(f"\n{result['medicine']}:")
        print(f"  Quantity: {result['quantity']}")
        print(f"  When to Take: {result['when_to_take']}")
        print(f"  Duration: {result['duration']}")


if __name__ == "__main__":
    test_extraction()
