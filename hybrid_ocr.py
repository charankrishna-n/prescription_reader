"""
hybrid_ocr.py
Hybrid OCR solution for prescription images:
1. CNN Model → Show your learning work (character-level)
2. Tesseract OCR → Get actual readable text
"""

import cv2
import numpy as np
import os
import sys

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import load_model, load_labels, clean_text
from ocr_pipeline import run_pipeline
from word_segmentation import run_word_pipeline


def install_tesseract():
    """Install pytesseract if not available."""
    try:
        import pytesseract
        return True
    except ImportError:
        print("[INFO] Installing pytesseract...")
        os.system("pip install pytesseract")
        try:
            import pytesseract
            return True
        except ImportError:
            print("[WARNING] Could not install pytesseract. OCR will be limited.")
            return False


def preprocess_for_tesseract(image_path):
    """Preprocess image specifically for Tesseract OCR."""
    img = cv2.imread(image_path)
    if img is None:
        return None
    
    # Resize for better OCR
    h, w = img.shape[:2]
    scale = 1500 / w  # Larger size for better OCR
    img = cv2.resize(img, (1500, int(h * scale)))
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Enhance contrast
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    
    # Denoise
    denoised = cv2.fastNlMeansDenoising(enhanced)
    
    # Sharpen
    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    sharpened = cv2.filter2D(denoised, -1, kernel)
    
    return sharpened


def run_tesseract_ocr(image_path):
    """Run Tesseract OCR on the image."""
    try:
        import pytesseract
        
        # Preprocess image
        processed = preprocess_for_tesseract(image_path)
        if processed is None:
            return "Error: Could not load image"
        
        # Try different OCR configurations
        configs = [
            '--psm 6',  # Uniform block of text
            '--psm 4',  # Single column of text
            '--psm 3',  # Fully automatic page segmentation
            '--psm 8',  # Single word
        ]
        
        results = []
        for config in configs:
            try:
                text = pytesseract.image_to_string(processed, config=config)
                if text.strip():
                    results.append(text.strip())
            except:
                continue
        
        if results:
            # Return the longest result (usually most complete)
            return max(results, key=len)
        else:
            return "No text detected by Tesseract"
            
    except ImportError:
        return "Tesseract not available"
    except Exception as e:
        return f"OCR Error: {str(e)}"


def run_hybrid_pipeline(image_path: str, model=None, label_map=None) -> dict:
    """
    Run both CNN-based character recognition and Tesseract OCR.
    Returns comprehensive results from both approaches.
    """
    results = {
        "image_path": image_path,
        "cnn_results": None,
        "word_results": None,
        "tesseract_results": None,
        "final_text": ""
    }
    
    print(f"[INFO] Processing: {os.path.basename(image_path)}")
    print("="*60)
    
    # 1. CNN Character Recognition (Your Learning Work)
    print("[1/3] Running CNN Character Recognition...")
    if model and label_map:
        try:
            cnn_result = run_pipeline(image_path, model, label_map, debug=False)
            results["cnn_results"] = cnn_result
            print(f"      Characters detected: {len(cnn_result.get('predictions', []))}")
            if cnn_result.get('predictions'):
                avg_conf = np.mean([c for _, c in cnn_result['predictions']])
                print(f"      Average confidence: {avg_conf:.3f}")
        except Exception as e:
            print(f"      CNN Error: {e}")
    else:
        print("      CNN model not loaded")
    
    # 2. Word-Level Segmentation
    print("[2/3] Running Word Segmentation...")
    try:
        word_result = run_word_pipeline(image_path)
        results["word_results"] = word_result
        print(f"      Words detected: {len(word_result.get('word_boxes', []))}")
    except Exception as e:
        print(f"      Word segmentation error: {e}")
    
    # 3. Tesseract OCR (Practical Solution)
    print("[3/3] Running Tesseract OCR...")
    tesseract_text = run_tesseract_ocr(image_path)
    results["tesseract_results"] = tesseract_text
    print(f"      Text length: {len(tesseract_text)} characters")
    
    # Determine final text
    if tesseract_text and len(tesseract_text) > 10 and "Error" not in tesseract_text:
        results["final_text"] = clean_text(tesseract_text)
    elif results["cnn_results"] and results["cnn_results"].get("cleaned_text"):
        results["final_text"] = results["cnn_results"]["cleaned_text"]
    else:
        results["final_text"] = "No readable text detected"
    
    return results


def display_results(results):
    """Display comprehensive results from all OCR methods."""
    print("\n" + "="*60)
    print("COMPREHENSIVE OCR RESULTS")
    print("="*60)
    
    # CNN Results
    print("\n🤖 CNN CHARACTER RECOGNITION (Your Learning Work)")
    print("-" * 50)
    cnn_results = results.get("cnn_results")
    if cnn_results:
        raw_text = cnn_results.get("raw_text", "")
        cleaned_text = cnn_results.get("cleaned_text", "")
        predictions = cnn_results.get("predictions", [])
        
        if predictions:
            print(f"Characters detected: {len(predictions)}")
            avg_conf = np.mean([c for _, c in predictions])
            print(f"Average confidence: {avg_conf:.3f}")
            
            # Show low confidence characters
            low_conf = [(i, char, conf) for i, (char, conf) in enumerate(predictions) if conf < 0.4]
            if low_conf:
                print(f"Low confidence chars: {len(low_conf)}")
        
        print(f"Raw text: {repr(raw_text)}")
        print(f"Cleaned text: {repr(cleaned_text)}")
    else:
        print("CNN recognition failed or not run")
    
    # Word Segmentation Results
    print("\n📝 WORD SEGMENTATION")
    print("-" * 50)
    word_results = results.get("word_results")
    if word_results:
        word_boxes = word_results.get("word_boxes", [])
        print(f"Words detected: {len(word_boxes)}")
        if word_boxes:
            avg_width = np.mean([w for _, _, w, _ in word_boxes])
            avg_height = np.mean([h for _, _, _, h in word_boxes])
            print(f"Average word size: {avg_width:.0f}x{avg_height:.0f} pixels")
    else:
        print("Word segmentation failed")
    
    # Tesseract Results
    print("\n🔍 TESSERACT OCR (Practical Solution)")
    print("-" * 50)
    tesseract_text = results.get("tesseract_results", "")
    if tesseract_text:
        print(f"Raw OCR text:\n{tesseract_text}")
    else:
        print("Tesseract OCR failed")
    
    # Final Result
    print("\n✅ FINAL EXTRACTED TEXT")
    print("=" * 50)
    final_text = results.get("final_text", "")
    print(final_text)
    
    return final_text


def save_visualizations(results, output_dir="test_images"):
    """Save visualization images from all methods."""
    saved_files = []
    
    # CNN visualization
    if results.get("cnn_results") and results["cnn_results"].get("visualisation") is not None:
        cnn_vis = results["cnn_results"]["visualisation"]
        cnn_path = os.path.join(output_dir, "output_cnn_chars.png")
        cv2.imwrite(cnn_path, cnn_vis)
        saved_files.append(cnn_path)
    
    # Word segmentation visualization
    if results.get("word_results") and results["word_results"].get("visualisation") is not None:
        word_vis = results["word_results"]["visualisation"]
        word_path = os.path.join(output_dir, "output_words.png")
        cv2.imwrite(word_path, word_vis)
        saved_files.append(word_path)
    
    return saved_files


def main():
    """Main function for hybrid OCR."""
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        # Auto-select first image
        test_dir = "test_images"
        images = [f for f in os.listdir(test_dir) 
                 if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff'))
                 and not f.startswith('output_')]
        if not images:
            print("[ERROR] No images found in test_images/")
            return
        image_path = os.path.join(test_dir, images[0])
    
    # Install Tesseract if needed
    install_tesseract()
    
    # Load CNN model (optional - for demonstration)
    model, label_map = None, None
    try:
        print("[INFO] Loading CNN model...")
        model = load_model("model.h5")
        label_map = load_labels("label_to_char_map.pkl")
        print(f"[INFO] CNN model loaded: {len(label_map)} classes")
    except Exception as e:
        print(f"[WARNING] Could not load CNN model: {e}")
    
    # Run hybrid pipeline
    results = run_hybrid_pipeline(image_path, model, label_map)
    
    # Display results
    final_text = display_results(results)
    
    # Save visualizations
    saved_files = save_visualizations(results)
    if saved_files:
        print(f"\n[INFO] Visualizations saved:")
        for f in saved_files:
            print(f"  → {f}")
    
    # Show images
    if results.get("word_results") and results["word_results"].get("visualisation") is not None:
        cv2.imshow("Word Segmentation", results["word_results"]["visualisation"])
    
    if results.get("cnn_results") and results["cnn_results"].get("visualisation") is not None:
        cv2.imshow("CNN Character Detection", results["cnn_results"]["visualisation"])
    
    print("\n[INFO] Press any key in image windows to exit.")
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    # Save final result to text file
    with open("test_images/extracted_text.txt", "w", encoding="utf-8") as f:
        f.write("PRESCRIPTION TEXT EXTRACTION RESULTS\n")
        f.write("="*50 + "\n\n")
        f.write(f"Image: {os.path.basename(image_path)}\n\n")
        f.write("FINAL EXTRACTED TEXT:\n")
        f.write("-"*30 + "\n")
        f.write(final_text + "\n\n")
        
        if results.get("tesseract_results"):
            f.write("RAW TESSERACT OUTPUT:\n")
            f.write("-"*30 + "\n")
            f.write(results["tesseract_results"] + "\n\n")
    
    print(f"[INFO] Results saved to: test_images/extracted_text.txt")


if __name__ == "__main__":
    main()