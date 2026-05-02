"""
simple_ocr.py
Simple, direct OCR solution for prescription images using Tesseract.
Focus on getting readable text rather than complex CNN processing.
"""

import cv2
import numpy as np
import os
import sys


def install_tesseract():
    """Install and configure Tesseract."""
    try:
        import pytesseract
        # Try to set Tesseract path for Windows
        try:
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        except:
            pass
        return True
    except ImportError:
        print("[INFO] Installing pytesseract...")
        os.system("pip install pytesseract")
        try:
            import pytesseract
            return True
        except ImportError:
            print("[ERROR] Could not install pytesseract")
            return False


def preprocess_image(image_path, method="default"):
    """
    Preprocess image for better OCR results.
    Try multiple preprocessing methods.
    """
    img = cv2.imread(image_path)
    if img is None:
        print(f"[ERROR] Cannot load image: {image_path}")
        return None
    
    print(f"[INFO] Original image size: {img.shape[1]}x{img.shape[0]}")
    
    # Convert to grayscale
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img.copy()
    
    if method == "default":
        # Simple resize and enhance
        h, w = gray.shape
        scale = 2000 / w  # Large size for better OCR
        new_w, new_h = int(w * scale), int(h * scale)
        resized = cv2.resize(gray, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
        
        # Enhance contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(resized)
        
        return enhanced
    
    elif method == "threshold":
        # Resize first
        h, w = gray.shape
        scale = 2000 / w
        resized = cv2.resize(gray, (int(w * scale), int(h * scale)))
        
        # Apply threshold
        _, thresh = cv2.threshold(resized, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return thresh
    
    elif method == "adaptive":
        # Resize
        h, w = gray.shape
        scale = 2000 / w
        resized = cv2.resize(gray, (int(w * scale), int(h * scale)))
        
        # Adaptive threshold
        adaptive = cv2.adaptiveThreshold(
            resized, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        return adaptive
    
    elif method == "denoise":
        # Resize and denoise
        h, w = gray.shape
        scale = 1500 / w
        resized = cv2.resize(gray, (int(w * scale), int(h * scale)))
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(resized)
        
        # Enhance
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)
        
        return enhanced


def run_tesseract_multiple_methods(image_path):
    """
    Try multiple preprocessing methods and OCR configurations.
    Return the best result.
    """
    try:
        import pytesseract
    except ImportError:
        return "Tesseract not available"
    
    print(f"[INFO] Running OCR on: {os.path.basename(image_path)}")
    
    # Different preprocessing methods
    methods = ["default", "threshold", "adaptive", "denoise"]
    
    # Different OCR configurations
    configs = [
        '--psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 ',
        '--psm 4',
        '--psm 3',
        '--psm 6',
        '--psm 8',
        '--psm 7',
    ]
    
    all_results = []
    
    for method in methods:
        print(f"  Trying preprocessing: {method}")
        processed = preprocess_image(image_path, method)
        
        if processed is None:
            continue
        
        # Save preprocessed image for inspection
        debug_path = f"test_images/debug_{method}.png"
        cv2.imwrite(debug_path, processed)
        
        for i, config in enumerate(configs):
            try:
                text = pytesseract.image_to_string(processed, config=config)
                text = text.strip()
                
                if text and len(text) > 3:  # Only keep meaningful results
                    confidence_score = len(text)  # Simple scoring
                    all_results.append({
                        'text': text,
                        'method': method,
                        'config': i,
                        'score': confidence_score
                    })
                    print(f"    Config {i}: Found {len(text)} chars")
            except Exception as e:
                continue
    
    if not all_results:
        return "No text detected with any method"
    
    # Return the result with highest score
    best_result = max(all_results, key=lambda x: x['score'])
    
    print(f"[INFO] Best result: {best_result['method']} + config {best_result['config']}")
    print(f"[INFO] Text length: {len(best_result['text'])} characters")
    
    return best_result['text']


def clean_ocr_text(text):
    """Clean and format OCR text for medical prescriptions."""
    if not text or len(text) < 3:
        return "No readable text found"
    
    # Basic cleaning
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        line = line.strip()
        if len(line) > 2:  # Keep lines with meaningful content
            # Remove excessive spaces
            line = ' '.join(line.split())
            cleaned_lines.append(line)
    
    cleaned_text = '\n'.join(cleaned_lines)
    
    # Medicine name correction (basic)
    medicine_corrections = {
        'paracetamol': ['paracetamol', 'paracetmol', 'paracetamo'],
        'augmentin': ['augmentin', 'augmentin', 'augmentin'],
        'pantoprazole': ['pantoprazole', 'pantoprazol', 'pantoprazole'],
        'amoxicillin': ['amoxicillin', 'amoxicilin', 'amoxicillin'],
    }
    
    # Simple word replacement
    words = cleaned_text.lower().split()
    corrected_words = []
    
    for word in words:
        corrected = word
        for correct_name, variants in medicine_corrections.items():
            for variant in variants:
                if variant in word.lower():
                    corrected = correct_name
                    break
        corrected_words.append(corrected)
    
    return ' '.join(corrected_words)


def main():
    """Main OCR function."""
    # Get image path
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        test_dir = "test_images"
        if not os.path.exists(test_dir):
            print(f"[ERROR] Directory {test_dir} not found")
            return
        
        images = [f for f in os.listdir(test_dir) 
                 if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff'))
                 and not f.startswith('output_') and not f.startswith('debug_')]
        
        if not images:
            print("[ERROR] No images found in test_images/")
            return
        
        image_path = os.path.join(test_dir, images[0])
    
    if not os.path.exists(image_path):
        print(f"[ERROR] Image not found: {image_path}")
        return
    
    print("="*60)
    print("SIMPLE OCR FOR PRESCRIPTION IMAGES")
    print("="*60)
    print(f"Image: {image_path}")
    
    # Install Tesseract
    if not install_tesseract():
        print("[ERROR] Cannot install Tesseract")
        return
    
    # Check if Tesseract is properly installed
    try:
        import pytesseract
        version = pytesseract.get_tesseract_version()
        print(f"[INFO] Tesseract version: {version}")
    except Exception as e:
        print(f"[WARNING] Tesseract issue: {e}")
        print("[INFO] You may need to install Tesseract separately:")
        print("  Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki")
        print("  Or try: winget install UB-Mannheim.TesseractOCR")
    
    # Run OCR
    print("\n" + "="*60)
    print("RUNNING OCR...")
    print("="*60)
    
    raw_text = run_tesseract_multiple_methods(image_path)
    cleaned_text = clean_ocr_text(raw_text)
    
    # Display results
    print("\n" + "="*60)
    print("RAW OCR OUTPUT")
    print("="*60)
    print(raw_text)
    
    print("\n" + "="*60)
    print("CLEANED TEXT")
    print("="*60)
    print(cleaned_text)
    
    # Save results
    with open("test_images/ocr_result.txt", "w", encoding="utf-8") as f:
        f.write("PRESCRIPTION OCR RESULTS\n")
        f.write("="*50 + "\n\n")
        f.write(f"Image: {os.path.basename(image_path)}\n\n")
        f.write("RAW OCR OUTPUT:\n")
        f.write("-"*30 + "\n")
        f.write(raw_text + "\n\n")
        f.write("CLEANED TEXT:\n")
        f.write("-"*30 + "\n")
        f.write(cleaned_text + "\n")
    
    print(f"\n[INFO] Results saved to: test_images/ocr_result.txt")
    print(f"[INFO] Debug images saved to: test_images/debug_*.png")
    
    # Show debug images
    debug_files = [f for f in os.listdir("test_images") if f.startswith("debug_")]
    if debug_files:
        print(f"[INFO] Check debug images to see preprocessing results:")
        for f in debug_files:
            print(f"  → test_images/{f}")


if __name__ == "__main__":
    main()