"""
test_extraction.py
Test script to demonstrate improved extraction of quantity, timing, and duration.
"""

from nlp_utils_improved import extract_details_linewise


def test_case_1():
    """Test basic prescription format."""
    print("\n" + "="*70)
    print("TEST CASE 1: Basic Prescription Format")
    print("="*70)
    
    text = """
    Tab Augmentin 625mg 1-0-1 x 5 days
    Tab Paracetamol 500mg 1-1-1 x 3 days
    """
    
    medicines = ["augmentin", "paracetamol"]
    results = extract_details_linewise(text, medicines)
    
    print("\nRESULTS:")
    for result in results:
        print(f"\n{result['medicine']}:")
        print(f"  Quantity: {result['quantity']}")
        print(f"  When to Take: {result['when_to_take']}")
        print(f"  Duration: {result['duration']}")


def test_case_2():
    """Test with spacing issues (common OCR errors)."""
    print("\n" + "="*70)
    print("TEST CASE 2: Spacing Issues (OCR Errors)")
    print("="*70)
    
    text = """
    Tab Augmentin 625 mg 1 - 0 - 1 x 5 days
    Tab Pantoprazole 40 mg 1 - 0 - 0 for 7 days
    """
    
    medicines = ["augmentin", "pantoprazole"]
    results = extract_details_linewise(text, medicines)
    
    print("\nRESULTS:")
    for result in results:
        print(f"\n{result['medicine']}:")
        print(f"  Quantity: {result['quantity']}")
        print(f"  When to Take: {result['when_to_take']}")
        print(f"  Duration: {result['duration']}")


def test_case_3():
    """Test with medical abbreviations."""
    print("\n" + "="*70)
    print("TEST CASE 3: Medical Abbreviations")
    print("="*70)
    
    text = """
    Tab Azithromycin 500mg BD x 3 days
    Tab Omeprazole 20mg OD x 14 days
    Tab Cetirizine 10mg TDS x 5 days
    """
    
    medicines = ["azithromycin", "omeprazole", "cetirizine"]
    results = extract_details_linewise(text, medicines)
    
    print("\nRESULTS:")
    for result in results:
        print(f"\n{result['medicine']}:")
        print(f"  Quantity: {result['quantity']}")
        print(f"  When to Take: {result['when_to_take']}")
        print(f"  Duration: {result['duration']}")


def test_case_4():
    """Test with different units (ml, g, mcg)."""
    print("\n" + "="*70)
    print("TEST CASE 4: Different Units (ml, g, mcg)")
    print("="*70)
    
    text = """
    Syrup Paracetamol 250ml 1-1-1 x 5 days
    Tab Insulin 10 units 1-0-1 x 30 days
    Tab Levothyroxine 50mcg 1-0-0 x 90 days
    """
    
    medicines = ["paracetamol", "insulin", "levothyroxine"]
    results = extract_details_linewise(text, medicines)
    
    print("\nRESULTS:")
    for result in results:
        print(f"\n{result['medicine']}:")
        print(f"  Quantity: {result['quantity']}")
        print(f"  When to Take: {result['when_to_take']}")
        print(f"  Duration: {result['duration']}")


def test_case_5():
    """Test with duration variations."""
    print("\n" + "="*70)
    print("TEST CASE 5: Duration Variations")
    print("="*70)
    
    text = """
    Tab Augmentin 625mg 1-0-1 for 5 days
    Tab Metformin 500mg 1-1-1 x 30 days
    Tab Atorvastatin 10mg 1-0-0 x 2 weeks
    Tab Warfarin 5mg 1-0-0 x 3 months
    """
    
    medicines = ["augmentin", "metformin", "atorvastatin", "warfarin"]
    results = extract_details_linewise(text, medicines)
    
    print("\nRESULTS:")
    for result in results:
        print(f"\n{result['medicine']}:")
        print(f"  Quantity: {result['quantity']}")
        print(f"  When to Take: {result['when_to_take']}")
        print(f"  Duration: {result['duration']}")


def test_case_6():
    """Test with missing fields (should show N/A)."""
    print("\n" + "="*70)
    print("TEST CASE 6: Missing Fields")
    print("="*70)
    
    text = """
    Tab Augmentin 625mg
    Tab Paracetamol 1-1-1
    Tab Ibuprofen x 5 days
    """
    
    medicines = ["augmentin", "paracetamol", "ibuprofen"]
    results = extract_details_linewise(text, medicines)
    
    print("\nRESULTS:")
    for result in results:
        print(f"\n{result['medicine']}:")
        print(f"  Quantity: {result['quantity']}")
        print(f"  When to Take: {result['when_to_take']}")
        print(f"  Duration: {result['duration']}")


if __name__ == "__main__":
    test_case_1()
    test_case_2()
    test_case_3()
    test_case_4()
    test_case_5()
    test_case_6()
    
    print("\n" + "="*70)
    print("ALL TESTS COMPLETED")
    print("="*70)
