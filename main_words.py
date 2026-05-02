"""
main_words.py
Word-level segmentation for handwritten prescriptions.

Usage:
    python main_words.py                        # first image in test_images/
    python main_words.py test_images/rx.jpg     # specific image
    python main_words.py test_images/rx.jpg --save-words  # save individual word images
"""

import sys
import os
import cv2

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

from word_segmentation import run_word_pipeline, save_word_images

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def main():
    args = sys.argv[1:]
    save_words = "--save-words" in args
    args = [a for a in args if a != "--save-words"]

    if args:
        image_path = args[0]
    else:
        test_dir = os.path.join(BASE_DIR, "test_images")
        images = [
            f for f in os.listdir(test_dir)
            if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".tiff"))
            and not f.startswith("output_") and not f.startswith("word_")
        ]
        if not images:
            print("[ERROR] No images found in test_images/.")
            sys.exit(1)
        image_path = os.path.join(test_dir, images[0])

    print(f"[INFO] Image: {image_path}")
    print(f"[INFO] Save individual words: {save_words}")

    # Run word-level pipeline
    result = run_word_pipeline(image_path)
    
    word_boxes = result["word_boxes"]
    word_images = result["word_images"]
    
    if not word_boxes:
        print("[INFO] No words detected.")
        return

    # Print word information
    print(f"\n{'='*50}")
    print("DETECTED WORDS")
    print(f"{'='*50}")
    for i, (x, y, w, h) in enumerate(word_boxes):
        print(f"Word {i+1:2d}: Box=({x:3d},{y:3d},{w:3d}x{h:2d})  Area={w*h:5d}px")

    # Save individual word images if requested
    if save_words and word_images:
        saved_paths = save_word_images(word_images)
        print(f"\n[INFO] Saved {len(saved_paths)} word images:")
        for path in saved_paths:
            print(f"  → {path}")

    # Show visualisation
    vis = result["visualisation"]
    cv2.imshow("Word Segmentation", vis)
    
    # Also show the processing steps
    char_binary = result["char_binary"]
    word_binary = result["word_binary"]
    
    # Create side-by-side comparison
    h, w = char_binary.shape
    comparison = np.zeros((h, w*2), dtype=np.uint8)
    comparison[:, :w] = char_binary
    comparison[:, w:] = word_binary
    
    cv2.imshow("Processing: Character Binary | Word Binary", comparison)
    
    # Save annotated result
    out_path = os.path.join(BASE_DIR, "test_images", "output_words.png")
    cv2.imwrite(out_path, vis)
    print(f"\n[INFO] Word segmentation result saved → {out_path}")
    
    print("\n[INFO] Press any key in the image windows to exit.")
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Summary
    print(f"\n{'='*50}")
    print("SUMMARY")
    print(f"{'='*50}")
    print(f"Words detected: {len(word_boxes)}")
    print(f"Average word width: {np.mean([w for _, _, w, _ in word_boxes]):.1f}px")
    print(f"Average word height: {np.mean([h for _, _, _, h in word_boxes]):.1f}px")
    
    print(f"\n{'='*50}")
    print("NEXT STEPS")
    print(f"{'='*50}")
    print("1. Check if word boxes look correct in the visualization")
    print("2. Use --save-words to inspect individual word images")
    print("3. For actual text recognition, consider:")
    print("   • OCR API (Google Vision, AWS Textract, Azure)")
    print("   • Tesseract OCR with handwriting models")
    print("   • Specialized medical prescription OCR services")


if __name__ == "__main__":
    import numpy as np
    main()