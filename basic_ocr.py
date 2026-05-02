"""
basic_ocr.py
Basic OCR solution that works without Tesseract installation.
Uses OpenCV for preprocessing and shows you exactly what's in your image.
"""

import cv2
import numpy as np
import os
import sys


def preprocess_and_analyze(image_path):
    """
    Preprocess image and analyze what's actually in it.
    This will help us understand why OCR is failing.
    """
    print(f"[INFO] Analyzing image: {os.path.basename(image_path)}")
    
    # Load image
    img = cv2.imread(image_path)
    if img is None:
        print(f"[ERROR] Cannot load image: {image_path}")
        return None
    
    print(f"[INFO] Original size: {img.shape[1]}x{img.shape[0]} pixels")
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Show basic statistics
    print(f"[INFO] Pixel intensity - Min: {gray.min()}, Max: {gray.max()}, Mean: {gray.mean():.1f}")
    
    # Try different preprocessing methods
    methods = {}
    
    # Method 1: Simple resize and enhance
    h, w = gray.shape
    scale = 1500 / w
    resized = cv2.resize(gray, (int(w * scale), int(h * scale)))
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(resized)
    methods['enhanced'] = enhanced
    
    # Method 2: Binary threshold
    _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    methods['binary'] = binary
    
    # Method 3: Adaptive threshold
    adaptive = cv2.adaptiveThreshold(
        enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 11, 2
    )
    methods['adaptive'] = adaptive
    
    # Method 4: Inverted adaptive (white text on black)
    adaptive_inv = cv2.adaptiveThreshold(
        enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY_INV, 11, 2
    )
    methods['adaptive_inv'] = adaptive_inv
    
    return methods


def analyze_text_regions(binary_img, method_name):
    """
    Analyze potential text regions in the binary image.
    """
    print(f"\n[INFO] Analyzing text regions in {method_name} image...")
    
    # Find contours
    contours, _ = cv2.findContours(binary_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    print(f"[INFO] Found {len(contours)} contours")
    
    # Analyze contour sizes
    areas = [cv2.contourArea(c) for c in contours]
    if areas:
        print(f"[INFO] Contour areas - Min: {min(areas):.0f}, Max: {max(areas):.0f}, Mean: {np.mean(areas):.0f}")
    
    # Filter contours by size (potential characters/words)
    text_contours = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        area = w * h
        
        # Filter criteria for text-like regions
        if (10 < w < 500 and 10 < h < 200 and 
            100 < area < 50000 and 
            0.1 < h/w < 10):  # Reasonable aspect ratio
            text_contours.append((x, y, w, h))
    
    print(f"[INFO] Potential text regions: {len(text_contours)}")
    
    return text_contours


def create_visualization(original_img, methods, text_regions_dict):
    """
    Create a comprehensive visualization of all processing steps.
    """
    # Resize original for display
    h, w = original_img.shape[:2]
    display_scale = 800 / w
    display_original = cv2.resize(original_img, (int(w * display_scale), int(h * display_scale)))
    
    visualizations = []
    
    for method_name, processed_img in methods.items():
        # Resize processed image for display
        vis_img = cv2.resize(processed_img, (display_original.shape[1], display_original.shape[0]))
        
        # Convert to color for drawing boxes
        if len(vis_img.shape) == 2:
            vis_img = cv2.cvtColor(vis_img, cv2.COLOR_GRAY2BGR)
        
        # Draw text region boxes if available
        if method_name in text_regions_dict:
            regions = text_regions_dict[method_name]
            for x, y, w, h in regions:
                # Scale coordinates
                x = int(x * display_scale)
                y = int(y * display_scale)
                w = int(w * display_scale)
                h = int(h * display_scale)
                
                cv2.rectangle(vis_img, (x, y), (x + w, y + h), (0, 255, 0), 1)
        
        # Add method name
        cv2.putText(vis_img, method_name.upper(), (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        visualizations.append(vis_img)
    
    return display_original, visualizations


def try_simple_ocr(image_path):
    """
    Try simple OCR using pytesseract if available, otherwise just analyze the image.
    """
    try:
        import pytesseract
        
        # Try to run Tesseract
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Simple preprocessing
        h, w = gray.shape
        scale = 1500 / w
        resized = cv2.resize(gray, (int(w * scale), int(h * scale)))
        
        # Try OCR
        text = pytesseract.image_to_string(resized)
        return text.strip() if text.strip() else "No text detected by Tesseract"
        
    except ImportError:
        return "Tesseract not available (pytesseract not installed)"
    except Exception as e:
        return f"OCR Error: {str(e)}"


def main():
    """Main function for basic OCR analysis."""
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
    print("BASIC OCR ANALYSIS")
    print("="*60)
    
    # Load and analyze image
    original = cv2.imread(image_path)
    methods = preprocess_and_analyze(image_path)
    
    if methods is None:
        return
    
    # Analyze text regions for each method
    text_regions_dict = {}
    for method_name, processed_img in methods.items():
        regions = analyze_text_regions(processed_img, method_name)
        text_regions_dict[method_name] = regions
        
        # Save processed image
        output_path = f"test_images/processed_{method_name}.png"
        cv2.imwrite(output_path, processed_img)
        print(f"[INFO] Saved: {output_path}")
    
    # Try OCR if available
    print("\n" + "="*60)
    print("OCR ATTEMPT")
    print("="*60)
    ocr_result = try_simple_ocr(image_path)
    print(f"OCR Result: {ocr_result}")
    
    # Create visualization
    display_original, visualizations = create_visualization(original, methods, text_regions_dict)
    
    # Show images
    cv2.imshow("Original Image", display_original)
    
    for i, (method_name, vis_img) in enumerate(zip(methods.keys(), visualizations)):
        cv2.imshow(f"Method: {method_name}", vis_img)
    
    # Save summary
    with open("test_images/analysis_report.txt", "w") as f:
        f.write("IMAGE ANALYSIS REPORT\n")
        f.write("="*50 + "\n\n")
        f.write(f"Image: {os.path.basename(image_path)}\n")
        f.write(f"Original size: {original.shape[1]}x{original.shape[0]}\n\n")
        
        for method_name, regions in text_regions_dict.items():
            f.write(f"{method_name.upper()} METHOD:\n")
            f.write(f"  Text regions found: {len(regions)}\n")
            if regions:
                avg_width = np.mean([w for _, _, w, _ in regions])
                avg_height = np.mean([h for _, _, _, h in regions])
                f.write(f"  Average region size: {avg_width:.0f}x{avg_height:.0f}\n")
            f.write("\n")
        
        f.write(f"OCR RESULT:\n{ocr_result}\n")
    
    print(f"\n[INFO] Analysis report saved: test_images/analysis_report.txt")
    print(f"[INFO] Processed images saved as: test_images/processed_*.png")
    print("\n[INFO] Press any key in the image windows to exit.")
    print("\nANALYSIS SUMMARY:")
    print("-" * 40)
    
    for method_name, regions in text_regions_dict.items():
        print(f"{method_name:12}: {len(regions):3d} text regions")
    
    print(f"\nBest method appears to be: {max(text_regions_dict.keys(), key=lambda k: len(text_regions_dict[k]))}")
    
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()