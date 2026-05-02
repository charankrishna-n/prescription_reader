"""
nlp_utils.py
NLP utilities for prescription text processing:
- Text cleaning
- Medicine name extraction
- Quantity (mg / ml / g) extraction
- When-to-take extraction (1-0-1 schedule + meal context)
- Duration extraction (x days, weeks)
"""

import re
import difflib
from typing import Dict, List, Tuple, Optional


# Medicine dictionary - expand as needed
MEDICINE_LIST = [
    "augmentin", "enzoflam", "pantoprazole", "hexigel", "paracetamol",
    "amoxicillin", "metformin", "atorvastatin", "omeprazole", "cetirizine",
    "azithromycin", "ibuprofen", "aspirin", "metronidazole", "ciprofloxacin",
    "diclofenac", "ranitidine", "losartan", "amlodipine", "hydrochlorothiazide",
    "prednisone", "warfarin", "insulin", "levothyroxine", "simvastatin"
]


def _build_when_to_take(dosage_code: Optional[str], meal_context: Optional[str]) -> str:
    """
    Combine a dosage schedule code (e.g. '1-0-1') with optional meal context
    (e.g. 'after meals') into a human-readable when_to_take string.

    Examples:
        '1-0-1', 'after meals'  -> '1-0-1 after meals'
        '1-1-1', None           -> '1-1-1'
        None,    'before meals' -> 'before meals'
        None,    None           -> 'N/A'
    """
    parts = []
    if dosage_code:
        parts.append(dosage_code)
    if meal_context:
        parts.append(meal_context)
    return " ".join(parts) if parts else "N/A"


class PrescriptionParser:
    def __init__(self, medicine_list=None):
        """
        Initialize prescription parser.

        Args:
            medicine_list: Custom list of medicine names (optional)
        """
        self.medicine_list = medicine_list or MEDICINE_LIST

    def clean_text(self, text: str) -> str:
        """
        Clean OCR text:
        - Convert to lowercase
        - Remove special characters except numbers, letters, spaces
        - Normalize spacing
        - Remove common OCR errors
        """
        if not text:
            return ""

        # Convert to lowercase
        text = text.lower()

        # Remove special characters but keep alphanumeric, spaces, and hyphens (for dosage patterns)
        text = re.sub(r'[^a-z0-9\s\-]', ' ', text)

        # Replace common OCR errors (numbers that look like letters)
        # 'l' (lowercase L) confused with '1' (one) - context-dependent
        # 'O' (letter O) confused with '0' (zero) - context-dependent
        
        # Normalize spacing (multiple spaces to single)
        text = re.sub(r'\s+', ' ', text)

        # Strip leading/trailing whitespace
        text = text.strip()

        return text

    def extract_medicines(self, text: str, cutoff: float = 0.6) -> List[Dict]:
        """
        Extract medicine names using fuzzy matching with EasyOCR output.

        Args:
            text: Cleaned OCR text
            cutoff: Similarity threshold for fuzzy matching (0-1), default 0.6

        Returns:
            List of dicts: [{"name": "medicine_name", "confidence": 0.85}, ...]
        """
        if not text:
            return []

        words = text.split()
        found_medicines = []
        found_names = set()  # Track found medicine names to avoid duplicates

        for word in words:
            # Skip very short words (less than 3 characters)
            if len(word) < 3:
                continue

            # Find best matches
            matches = difflib.get_close_matches(
                word,
                self.medicine_list,
                n=1,
                cutoff=cutoff
            )

            if matches:
                medicine_name = matches[0]
                
                # Skip if already found (avoid duplicates in order)
                if medicine_name in found_names:
                    continue
                    
                found_names.add(medicine_name)
                
                # Calculate similarity score
                similarity = difflib.SequenceMatcher(None, word, medicine_name).ratio()
                found_medicines.append({
                    "name": medicine_name,
                    "confidence": round(similarity, 2),
                    "original_word": word
                })

        return found_medicines

    def extract_dosage(self, text: str) -> Dict:
        """
        Extract dosage information using regex patterns.

        Returns:
            Dict with keys: dosage, frequency, duration, strength
        """
        result = {
            "dosage": None,
            "frequency": None,
            "duration": None,
            "strength": None
        }

        # Pattern for dosage frequency like "1-0-1" or "1-1-1"
        dosage_pattern = r'\b(\d-\d-\d)\b'
        dosage_match = re.search(dosage_pattern, text)
        if dosage_match:
            result["dosage"] = dosage_match.group(1)

        # Pattern for frequency like "twice daily", "three times", etc.
        freq_patterns = [
            r'\b(\d+)\s*times?\s*(?:a|per)\s*day\b',
            r'\b(twice|thrice|once|three\s*times|four\s*times)\s*(?:daily|day|per\s*day)\b',
            r'\b(morning|afternoon|evening|night)\b'
        ]

        for pattern in freq_patterns:
            freq_match = re.search(pattern, text, re.IGNORECASE)
            if freq_match:
                result["frequency"] = freq_match.group(1)
                break

        # Pattern for duration like "x 5 days", "for 7 days", "5 days course"
        duration_patterns = [
            r'\b(?:x|for|×)\s*(\d+)\s*(days?|weeks?|months?)\b',
            r'\b(\d+)\s*(days?|weeks?|months?)\s*(?:course|treatment)\b'
        ]

        for pattern in duration_patterns:
            duration_match = re.search(pattern, text, re.IGNORECASE)
            if duration_match:
                result["duration"] = f"{duration_match.group(1)} {duration_match.group(2)}"
                break

        # Pattern for strength like "625mg", "500 mg", "10ml"
        strength_pattern = r'\b(\d+(?:\.\d+)?)\s*(mg|ml|g|mcg|units?)\b'
        strength_match = re.search(strength_pattern, text, re.IGNORECASE)
        if strength_match:
            result["strength"] = f"{strength_match.group(1)}{strength_match.group(2)}"

        return result

    # ── Abbreviation → internal dosage code ─────────────────────────────────
    _ABBREV_MAP = {
        # Standard medical frequency abbreviations
        "od":    "1-0-0",  "o.d.": "1-0-0",  "once":   "1-0-0",
        "bd":    "1-0-1",  "b.d.": "1-0-1",  "bid":    "1-0-1",  "b.i.d.": "1-0-1",
        "tds":   "1-1-1",  "t.d.s.": "1-1-1", "tid":   "1-1-1",  "t.i.d.": "1-1-1",
        "qid":   "1-1-1",  "q.i.d.": "1-1-1",
        "hs":    "0-0-1",  "h.s.": "0-0-1",  "sos":   "0-0-1",
    }

    def extract_dosage_from_segment(self, segment: str) -> Dict:
        """
        Extract dosage info from a small text segment.
        Handles: 1-0-1 patterns, OD/BD/TDS/QID/HS abbreviations,
                 text phrases (once daily, twice a day, morning & night, etc.),
                 duration (x5 days, for 1 week, 5/7), strength (mg/ml/g).
        """
        result = {"dosage": None, "duration": None, "strength": None}
        seg_low = segment.lower()

        # ── 1. Numeric 1-0-1 style ────────────────────────────────────────────
        # Normalise spaces around hyphens and fix OCR noise ('e' near digits → '1')
        seg_norm = re.sub(r'\s*-\s*', '-', segment)
        seg_norm = re.sub(r'(?<=[0-9-])e(?=[0-9-]|\b)', '1', seg_norm, flags=re.IGNORECASE)

        dosage_3 = re.search(r'\b([01][\-]?[01][\-]?[01])\b', seg_norm)
        dosage_2 = re.search(r'\b([01])[-]([01])\b', seg_norm)

        if dosage_3:
            raw = dosage_3.group(1)
            if '-' not in raw:
                raw = raw[0] + '-' + raw[1] + '-' + (raw[2] if len(raw) > 2 else '0')
            result["dosage"] = raw
        elif dosage_2:
            result["dosage"] = dosage_2.group(1) + '-0-' + dosage_2.group(2)

        # ── 2. Medical abbreviations (OD, BD, TDS …) ─────────────────────────
        if result["dosage"] is None:
            for abbr, code in self._ABBREV_MAP.items():
                if re.search(r'\b' + re.escape(abbr) + r'\b', seg_low):
                    result["dosage"] = code
                    break

        # ── 3. Text-based frequency phrases ──────────────────────────────────
        if result["dosage"] is None:
            text_map = [
                (r'three\s*times|thrice|t\.d\.s', "1-1-1"),
                (r'twice|two\s*times|b\.d|2\s*times', "1-0-1"),
                (r'once|one\s*time|daily|o\.d', "1-0-0"),
                (r'(at\s*)?bed\s*time|at\s*night|night\s*only|h\.s', "0-0-1"),
                (r'morning\s*(and|&|\+)\s*(evening|night)', "1-0-1"),
                (r'morning\s*(and|&|\+)\s*afternoon', "1-1-0"),
                (r'afternoon\s*(and|&|\+)\s*(evening|night)', "0-1-1"),
                (r'morning', "1-0-0"),
                (r'evening|night', "0-0-1"),
            ]
            for pattern, code in text_map:
                if re.search(pattern, seg_low):
                    result["dosage"] = code
                    break

        # ── 4. Duration ───────────────────────────────────────────────────────
        duration_patterns = [
            r'[xX×]\s*(\d+)\s*(days?|weeks?|months?)',   # x5 days
            r'for\s+(\d+)\s*(days?|weeks?|months?)',      # for 5 days
            r'(\d+)\s*/\s*7',                             # 5/7 = 5 days
            r'(\d+)\s*/\s*52',                            # 2/52 = 2 weeks
            r'(\d+)\s*/\s*12',                            # 1/12 = 1 month
            r'\b(\d+)\s*(days?|weeks?|months?)\b',        # 5 days
            r'(\d+)\s*d\b',                               # 5d
        ]
        slot_map = {'/7': 'days', '/52': 'weeks', '/12': 'months'}
        for pat in duration_patterns:
            m = re.search(pat, segment, re.IGNORECASE)
            if m:
                num = m.group(1)
                # normalise shorthand /7, /52, /12
                unit = m.group(2) if m.lastindex >= 2 else 'days'
                for k, v in slot_map.items():
                    if k in pat:
                        unit = v
                        break
                if 'd\\b' in pat:   # '5d' shorthand
                    unit = 'days'
                result["duration"] = f"{num} {unit}"
                break

        # ── 5. Strength / Quantity ────────────────────────────────────────────
        # Handles: 625mg, 500 mg, 10 ml, 1g, 250mcg, noisy OCR with spaces
        strength_pat = re.compile(
            r'(\d+(?:\.\d+)?)\s*(mg|ml|g\b|mcg|units?|iu|tab(?:let)?s?)',
            re.IGNORECASE
        )
        # Prefer the first match that contains a standard drug unit (not just 'tab')
        strength_found = None
        for sm in strength_pat.finditer(segment):
            unit = sm.group(2).lower()
            if unit in ('mg', 'ml', 'g', 'mcg', 'units', 'unit', 'iu'):
                strength_found = f"{sm.group(1)}{unit}"
                break
            elif strength_found is None:   # fallback: tab/tablet count
                strength_found = f"{sm.group(1)} {sm.group(2).lower()}"
        if strength_found:
            result["strength"] = strength_found

        # ── 6. Meal context ───────────────────────────────────────────────────
        meal_patterns = [
            (r'\bafter\s*meals?\b',          'after meals'),
            (r'\bbefore\s*meals?\b',         'before meals'),
            (r'\bwith\s*(?:food|meals?)\b',  'with food'),
            (r'\bon\s*(?:empty|empty\s*stomach)\b', 'on empty stomach'),
            (r'\bpc\b',                      'after meals'),   # medical abbrev
            (r'\bac\b',                      'before meals'),  # medical abbrev
            (r'\bcc\b',                      'with food'),     # cum cibo
        ]
        result["meal_context"] = None
        for pat, label in meal_patterns:
            if re.search(pat, segment, re.IGNORECASE):
                result["meal_context"] = label
                break

        return result

    def parse_prescription_linewise(self, ocr_text: str) -> Dict:
        """
        Parse prescription by splitting into lines and extracting dosage from
        the window of lines immediately following each detected medicine.
        This gives each medicine its own correct dosage schedule.
        """
        lines = ocr_text.splitlines()
        cleaned_text = self.clean_text(ocr_text)

        # ── Medicine detection ────────────────────────────────────────────────
        # Pass 1: fuzzy match against known medicine list
        found_medicines = []
        found_names = set()

        for line_idx, line in enumerate(lines):
            for word in line.split():
                word_clean = re.sub(r'[^a-zA-Z]', '', word).lower()
                if len(word_clean) < 3:
                    continue
                matches = difflib.get_close_matches(word_clean, self.medicine_list, n=1, cutoff=0.6)
                if matches:
                    med_name = matches[0]
                    if med_name in found_names:
                        continue
                    found_names.add(med_name)
                    similarity = difflib.SequenceMatcher(None, word_clean, med_name).ratio()
                    found_medicines.append({
                        "name":          med_name,
                        "confidence":    round(similarity, 2),
                        "original_word": word,
                        "line_idx":      line_idx,
                    })

        # Pass 2: capture any word that follows Tab/Cap/Syp/Inj/Inj. prefix
        # This catches medicines not in our list but clearly marked by the doctor.
        prefix_pat = re.compile(
            r'\b(?:Tab\.?|Cap\.?|Syp\.?|Syr\.?|Inj\.?|Drops?|Oint\.?|Gel\.?)\s+([A-Z][a-zA-Z]+)',
            re.IGNORECASE
        )
        for line_idx, line in enumerate(lines):
            for m in prefix_pat.finditer(line):
                cand = m.group(1).lower()
                # skip if already found via fuzzy match
                already = any(med["name"] == cand or
                              difflib.SequenceMatcher(None, cand, med["name"]).ratio() > 0.8
                              for med in found_medicines)
                if not already and cand not in found_names:
                    found_names.add(cand)
                    found_medicines.append({
                        "name":          cand,
                        "confidence":    0.75,
                        "original_word": m.group(1),
                        "line_idx":      line_idx,
                    })

        # Sort by line order
        found_medicines.sort(key=lambda x: x["line_idx"])

        # For each medicine, extract dosage/duration from the lines below,
        # but strength only from the medicine's OWN line.
        # CRITICAL: stop the window at the NEXT medicine's line so we never
        # accidentally read another medicine's dosage schedule.
        parsed_medicines = []
        for i, med in enumerate(found_medicines):
            own_line = lines[med["line_idx"]]

            # Window starts on the line after the medicine name
            start = med["line_idx"] + 1

            # Window ends just before the next medicine's line (or +7 max)
            if i + 1 < len(found_medicines):
                next_med_line = found_medicines[i + 1]["line_idx"]
                end = min(next_med_line, med["line_idx"] + 7)
            else:
                end = min(med["line_idx"] + 7, len(lines))

            below = "\n".join(lines[start:end])

            # ── Quantity / Strength: own line first, then below lines ──────────
            # Combine own_line + below for strength search (handles next-line cases)
            full_window = own_line + "\n" + below
            own_info    = self.extract_dosage_from_segment(own_line)
            strength    = own_info.get("strength")  # prefer own line

            # Dosage schedule + duration + meal context: from lines immediately below
            below_info = self.extract_dosage_from_segment(below)

            if strength is None:
                strength = below_info.get("strength")  # fallback: look below

            # Also check the raw full window for strength (handles spaces in OCR)
            if strength is None:
                win_info = self.extract_dosage_from_segment(full_window)
                strength = win_info.get("strength")

            # ── Duration fallback ─────────────────────────────────────────────
            duration = below_info["duration"]
            if duration is None:
                if i + 1 < len(found_medicines):
                    fallback_end = min(found_medicines[i + 1]["line_idx"] + 2, len(lines))
                else:
                    fallback_end = min(med["line_idx"] + 10, len(lines))
                fallback_seg = "\n".join(lines[start:fallback_end])
                fallback_info = self.extract_dosage_from_segment(fallback_seg)
                duration = fallback_info["duration"]

            # ── Meal context fallback ─────────────────────────────────────────
            meal_context = below_info.get("meal_context")
            if meal_context is None:
                meal_context = own_info.get("meal_context")
            if meal_context is None:
                # Broader window: search the full text around the medicine
                win_info2 = self.extract_dosage_from_segment(full_window)
                meal_context = win_info2.get("meal_context")

            # ── Build combined when_to_take ───────────────────────────────────
            dosage_code = below_info.get("dosage") or own_info.get("dosage")
            when_to_take = _build_when_to_take(dosage_code, meal_context)

            parsed_medicines.append({
                "medicine":     med["name"].title(),
                "quantity":     strength,        # e.g. "625mg"
                "dosage":       dosage_code,     # e.g. "1-0-1"
                "when_to_take": when_to_take,    # e.g. "1-0-1 after meals"
                "meal_context": meal_context,    # e.g. "after meals"
                "strength":     strength,        # kept for backward compat
                "duration":     duration,         # e.g. "5 days"
                "confidence":   med["confidence"],
            })


        # Global fallback for fields not found per-medicine
        global_dosage = self.extract_dosage(cleaned_text)

        # Fill in any N/A fields using global fallback values
        global_strength = global_dosage.get("strength")
        global_duration = global_dosage.get("duration")
        global_dose_code = global_dosage.get("dosage")

        for med in parsed_medicines:
            if med["quantity"] is None and global_strength:
                med["quantity"] = global_strength
                med["strength"] = global_strength
            if med["duration"] is None and global_duration:
                med["duration"] = global_duration
            if med["dosage"] is None and global_dose_code:
                med["dosage"] = global_dose_code
                med["when_to_take"] = _build_when_to_take(global_dose_code, med.get("meal_context"))

        return {
            "raw_text":         ocr_text,
            "cleaned_text":     cleaned_text,
            "medicines":        [{"name": m["name"], "confidence": m["confidence"],
                                  "original_word": m["original_word"]}
                                 for m in found_medicines],
            "dosage_info":      global_dosage,
            "parsed_medicines": parsed_medicines,
        }

    def parse_prescription(self, ocr_text: str) -> Dict:
        """
        Complete prescription parsing pipeline — delegates to linewise parser.
        """
        return self.parse_prescription_linewise(ocr_text)

    def add_medicine(self, medicine_name: str):
        """Add a new medicine to the dictionary."""
        if medicine_name.lower() not in [m.lower() for m in self.medicine_list]:
            self.medicine_list.append(medicine_name.lower())

    def get_medicine_list(self) -> List[str]:
        """Get current medicine list."""
        return self.medicine_list.copy()


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


def test_parser():
    """Test function for prescription parser."""
    parser = PrescriptionParser()

    # Test text
    test_text = "Tab Augmentin 625mg 1-0-1 x 5 days"

    result = parser.parse_prescription(test_text)

    print("Raw Text:", result["raw_text"])
    print("Cleaned Text:", result["cleaned_text"])
    print("Medicines Found:", result["medicines"])
    print("Dosage Info:", result["dosage_info"])
    print("\nParsed Medicines:")
    for med in result["parsed_medicines"]:
        print(f"- {med}")


if __name__ == "__main__":
    test_parser()