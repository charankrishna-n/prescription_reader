"""
prescription_pipeline.py
Full prescription processing pipeline:
    1. Gemini 2.5 Pro image understanding → extract structured medicine data
"""

import os
import sys

# Force UTF-8 output on Windows to handle non-ASCII characters in prescription text
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from gemini_vision import extract_prescription_with_gemini


# ---------------------------------------------------------------------------
# Optional: expand this list with more medicines as needed
# ---------------------------------------------------------------------------
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
    log(f"  PRESCRIPTION PIPELINE")
    log(f"  Image : {image_path}")
    log(f"{'='*55}")

    # ── Step 1: Gemini image understanding ────────────────────────────────
    log("\n[1/2] Extracting structured data with Gemini 2.5 Pro...")
    try:
        gemini_result = extract_prescription_with_gemini(image_path)
    except FileNotFoundError as e:
        print(f"  [ERROR] {e}")
        return {"error": str(e)}
    except ValueError as e:
        print(f"  [ERROR] Configuration error → {e}")
        return {"error": f"Configuration error: {e}"}
    except Exception as e:
        print(f"  [ERROR] Gemini extraction failed → {e}")
        return {"error": f"Gemini extraction failed: {str(e)}"}

    raw_text = gemini_result.get("raw_text", "")
    parsed_medicines = gemini_result.get("parsed_medicines", [])

    if not raw_text.strip():
        raw_text = ""

    log(f"  [OK] Extracted {len(parsed_medicines)} medicine rows")
    log(f"  Preview : {raw_text[:120].strip()}{'...' if len(raw_text) > 120 else ''}")

    # ── Step 2: Normalise output for API contract ────────────────────────
    log("\n[2/2] Normalising output...")

    medicines = parsed_medicines
    cleaned_text = raw_text.lower().strip() if raw_text else ""
    dosage_info = {}

    # ── Print results (clean, minimal) ───────────────────────────────────
    log("")
    log("  Detected Medicines")
    log("  " + "-" * 40)

    if medicines:
        for i, med in enumerate(medicines, 1):
            name         = med.get("medicine", "Unknown")
            quantity     = med.get("quantity") or med.get("strength") or "N/A"
            when_to_take = med.get("when_to_take") or dosage_to_timing(med.get("dosage") or "")
            duration     = med.get("duration") or "N/A"
            log(f"  {i}. {name}")
            log(f"     Quantity    : {quantity}")
            log(f"     When to Take: {when_to_take}")
            log(f"     Duration    : {duration}")
            log("")
    else:
        log("  No medicines detected.")
        log("  Tip: Add medicine names to EXTENDED_MEDICINE_LIST in prescription_pipeline.py")
        log("")

    return {
        "raw_text":         raw_text,
        "cleaned_text":     cleaned_text,
        "medicines":        [
            {
                "name": med.get("medicine", "Unknown"),
                "confidence": med.get("confidence", 0.0),
                "original_word": med.get("medicine", "Unknown"),
            }
            for med in medicines
        ],
        "dosage_info":      dosage_info,
        "parsed_medicines": medicines,                 # structured entries with quantity, when_to_take, duration
    }


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        # Default: use first image in test_images/
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
            print("        python prescription_pipeline.py path/to/image.jpg")
            sys.exit(1)
    else:
        image_path = sys.argv[1]

    result = run_pipeline(image_path, verbose=True)

    if "error" in result:
        sys.exit(1)
