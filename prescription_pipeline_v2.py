"""
prescription_pipeline_v2.py
Full prescription processing pipeline with improved extraction:
  1. Google Vision API  →  extract raw text from image
  2. NLP cleaning       →  lowercase, normalise spacing
  3. Medicine detection →  fuzzy match against medicine dictionary
  4. Dosage extraction  →  strength, frequency, duration (IMPROVED)
"""

import os
import sys

# Force UTF-8 output on Windows to handle non-ASCII characters in prescription text
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from google.api_core.exceptions import GoogleAPIError
from vision_api import extract_text_from_image, clean_extracted_text
from nlp_utils import PrescriptionParser
from nlp_utils_improved import extract_details_linewise


EXTENDED_MEDICINE_LIST = [
    # Antibiotics
    "augmentin", "amoxicillin", "azithromycin", "ciprofloxacin",
    "metronidazole", "doxycycline", "clindamycin", "cephalexin",
    # Pain / Fever
    "paracetamol", "ibuprofen", "aspirin", "diclofenac", "enzoflam",
    "naproxen", "tramadol", "ketorolac", "dolo", "calpol", "combiflam",
    # Stomach / Acid
    "pantoprazole", "omeprazole", "ranitidine", "domperidone",
    "ondansetron", "metoclopramide", "pand", "pantocid",
    "rantac", "nexpro", "rabeprazole",
    # Allergy
    "cetirizine", "loratadine", "fexofenadine", "chlorpheniramine",
    "allegra", "montair", "montelukast",
    # BP / Heart
    "amlodipine", "losartan", "atenolol", "metoprolol",
    "hydrochlorothiazide", "enalapril", "ramipril",
    # Diabetes
    "metformin", "insulin", "glipizide", "sitagliptin", "glycomet",
    # Cholesterol
    "atorvastatin", "simvastatin", "rosuvastatin",
    # Thyroid
    "levothyroxine", "eltroxin", "thyronorm",
    # Steroids
    "prednisone", "dexamethasone", "prednisolone",
    # Blood thinners
    "warfarin", "clopidogrel", "ecosprin",
    # Vitamins / Supplements
    "shelcal", "zincovit",
    # Mouth / Topical
    "hexigel", "betadine", "clotrimazole",
]


def dosage_to_timing(dosage_str: str) -> str:
    """
    Convert a dosage schedule like '1-0-1' into a human-readable timing string.

    Format: Morning - Afternoon - Night  (1 = take, 0 = skip)
    Examples:
        '1-1-1'  ->  'Morning, Afternoon & Night'
        '1-0-1'  ->  'Morning & Night'
        '1-0-0'  ->  'Morning only'
        '0-1-0'  ->  'Afternoon only'
        '0-0-1'  ->  'Night only'
        '1-1-0'  ->  'Morning & Afternoon'
        '0-1-1'  ->  'Afternoon & Night'
    """
    if not dosage_str:
        return "N/A"

    parts = dosage_str.strip().split("-")
    if len(parts) != 3:
        return dosage_str  # return as-is if pattern doesn't match

    slots = {"Morning": parts[0], "Afternoon": parts[1], "Night": parts[2]}
    active = [time for time, val in slots.items() if val.strip() not in ("", "0")]

    if not active:
        return "N/A"
    if len(active) == 1:
        return f"{active[0]} only"
    if len(active) == 2:
        return f"{active[0]} & {active[1]}"
    return "Morning, Afternoon & Night"


def run_pipeline(image_path: str, verbose: bool = True) -> dict:
    """
    Run the full prescription OCR + medicine detection pipeline.

    Args:
        image_path: Path to the prescription image.
        verbose:    Print step-by-step progress to the console.

    Returns:
        Dict with keys:
            raw_text        – text straight from Vision API
            cleaned_text    – normalised lowercase text
            medicines       – list of {name, confidence, original_word}
            dosage_info     – {strength, dosage, frequency, duration}
            parsed_medicines – structured list of detected medicine entries
            error           – set only if something went wrong
    """

    def log(msg: str):
        if verbose:
            print(msg)

    log(f"\n{'='*55}")
    log(f"  PRESCRIPTION PIPELINE (IMPROVED)")
    log(f"  Image : {image_path}")
    log(f"{'='*55}")

    # ── Step 1: Vision API OCR ────────────────────────────────────────────
    log("\n[1/3] Extracting text with Google Vision API...")
    try:
        raw_text = extract_text_from_image(image_path)
    except FileNotFoundError as e:
        print(f"  [ERROR] {e}")
        return {"error": str(e)}
    except GoogleAPIError as e:
        print(f"  [ERROR] Vision API failed → {e}")
        return {"error": str(e)}

    if not raw_text.strip():
        log("  [WARNING] No text found in image.")
        return {
            "raw_text": "",
            "cleaned_text": "",
            "medicines": [],
            "dosage_info": {},
            "parsed_medicines": [],
        }

    log(f"  [OK] Extracted {len(raw_text)} characters")
    log(f"  Preview : {raw_text[:120].strip()}{'...' if len(raw_text) > 120 else ''}")

    # ── Step 2: Clean text ────────────────────────────────────────────────
    log("\n[2/3] Cleaning and normalising text...")
    cleaned_text = clean_extracted_text(raw_text)
    log(f"  [OK] Cleaned : {cleaned_text[:120]}{'...' if len(cleaned_text) > 120 else ''}")

    # ── Step 3: Medicine + dosage detection ──────────────────────────────
    log("\n[3/3] Detecting medicines and dosage information...")
    parser = PrescriptionParser(medicine_list=EXTENDED_MEDICINE_LIST)
    result = parser.parse_prescription(raw_text)

    medicines = result["parsed_medicines"]
    dosage_info = result["dosage_info"]

    # Use improved line-based extraction for better accuracy
    medicine_names = [m["name"].lower() for m in result["medicines"]]
    if medicine_names:
        log("\n  [DEBUG] Running improved line-based extraction...")
        improved_results = extract_details_linewise(raw_text, medicine_names)
        # Merge improved results back into parsed_medicines
        for i, med in enumerate(medicines):
            if i < len(improved_results):
                improved = improved_results[i]
                if improved["quantity"] != "N/A":
                    med["quantity"] = improved["quantity"]
                    med["strength"] = improved["quantity"]
                if improved["when_to_take"] != "N/A":
                    med["when_to_take"] = improved["when_to_take"]
                if improved["duration"] != "N/A":
                    med["duration"] = improved["duration"]

    # ── Print results (clean, minimal) ───────────────────────────────────
    log("")
    log("  Detected Medicines")
    log("  " + "-" * 40)

    if medicines:
        for i, med in enumerate(medicines, 1):
            name = med.get("medicine", "Unknown")
            quantity = med.get("quantity") or med.get("strength") or "N/A"
            when_to_take = med.get("when_to_take") or dosage_to_timing(med.get("dosage") or "")
            duration = med.get("duration") or "N/A"
            log(f"  {i}. {name}")
            log(f"     Quantity    : {quantity}")
            log(f"     When to Take: {when_to_take}")
            log(f"     Duration    : {duration}")
            log("")
    else:
        log("  No medicines detected.")
        log("  Tip: Add medicine names to EXTENDED_MEDICINE_LIST in prescription_pipeline_v2.py")
        log("")

    return {
        "raw_text": raw_text,
        "cleaned_text": cleaned_text,
        "medicines": result["medicines"],
        "dosage_info": dosage_info,
        "parsed_medicines": medicines,
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        test_dir = "test_images"
        if os.path.isdir(test_dir):
            candidates = [
                f for f in os.listdir(test_dir)
                if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".tiff"))
            ]
            if candidates:
                image_path = os.path.join(test_dir, candidates[0])
            else:
                print("[ERROR] No images found in test_images/")
                sys.exit(1)
        else:
            print("[ERROR] Provide an image path:")
            print("        python prescription_pipeline_v2.py path/to/image.jpg")
            sys.exit(1)
    else:
        image_path = sys.argv[1]

    result = run_pipeline(image_path, verbose=True)

    if "error" in result:
        sys.exit(1)
