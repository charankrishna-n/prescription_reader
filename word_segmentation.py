"""
word_segmentation.py
Word-level segmentation for handwritten prescriptions with connected characters.
"""

import cv2
import numpy as np


def preprocess_for_words(image_path: str):
    """
    Preprocess image for word-level segmentation.
    Returns (original, binary, word_binary).
    """
    original = cv2.imread(image_path)
    if original is None:
        raise FileNotFoundError(f"Cannot open image: {image_path}")

    # Resize to reasonable size
    h, w = original.shape[:2]
    scale = 1000 / w
    original = cv2.resize(original, (1000, int(h * scale)))

    gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)

    # Light preprocessing
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    
    # Gentle blur
    blurred = cv2.GaussianBlur(enhanced, (3, 3), 0)

    # Adaptive threshold for character detection
    char_binary = cv2.adaptiveThreshold(
        blurred, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        blockSize=11, C=2
    )

    # WORD-LEVEL PROCESSING: Dilate horizontally to connect letters into words
    # Horizontal kernel to merge characters in the same word
    kernel_word = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 5))
    word_binary = cv2.dilate(char_binary, kernel_word, iterations=1)
    
    # Clean up small noise
    kernel_clean = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    word_binary = cv2.morphologyEx(word_binary, cv2.MORPH_OPEN, kernel_clean)

    return original, char_binary, word_binary


def segment_words(word_binary):
    """
    Find word-level bounding boxes.
    Returns list of (x, y, w, h) sorted top-to-bottom, left-to-right.
    """
    contours, _ = cv2.findContours(
        word_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    word_boxes = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        
        # Filter word boxes
        if w < 30 or h < 15:    # too small → noise
            continue
        if w > 800 or h > 200:  # too large → entire line or image
            continue
        if w < h:               # too tall → likely vertical artifact
            continue
            
        word_boxes.append((x, y, w, h))

    if not word_boxes:
        return []

    # Sort by Y (line-wise) then by X (left-to-right)
    LINE_TOLERANCE = 30
    
    boxes_sorted_y = sorted(word_boxes, key=lambda b: b[1])
    lines = []
    current_line = [boxes_sorted_y[0]]

    for box in boxes_sorted_y[1:]:
        prev_cy = current_line[-1][1] + current_line[-1][3] / 2
        curr_cy = box[1] + box[3] / 2
        if abs(curr_cy - prev_cy) <= LINE_TOLERANCE:
            current_line.append(box)
        else:
            lines.append(sorted(current_line, key=lambda b: b[0]))
            current_line = [box]
    lines.append(sorted(current_line, key=lambda b: b[0]))

    # Flatten back to sorted list
    sorted_boxes = [box for line in lines for box in line]
    return sorted_boxes


def extract_word_images(original, word_boxes):
    """
    Extract individual word images from the original.
    Returns list of cropped word images.
    """
    word_images = []
    for i, (x, y, w, h) in enumerate(word_boxes):
        # Add small padding
        pad = 5
        x1 = max(0, x - pad)
        y1 = max(0, y - pad)
        x2 = min(original.shape[1], x + w + pad)
        y2 = min(original.shape[0], y + h + pad)
        
        word_img = original[y1:y2, x1:x2]
        word_images.append(word_img)
    
    return word_images


def draw_word_boxes(original, word_boxes):
    """Draw bounding boxes around detected words."""
    vis = original.copy()
    for i, (x, y, w, h) in enumerate(word_boxes):
        # Draw word box in green
        cv2.rectangle(vis, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        # Label with word number
        cv2.putText(vis, f"W{i+1}", (x, y - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                    (0, 255, 0), 2, cv2.LINE_AA)
    
    return vis


def run_word_pipeline(image_path: str) -> dict:
    """
    Word-level segmentation pipeline.
    Returns dict with word_boxes, word_images, visualisation.
    """
    print("[INFO] Running WORD-LEVEL segmentation...")
    
    # 1. Preprocess
    original, char_binary, word_binary = preprocess_for_words(image_path)
    
    # 2. Segment words
    word_boxes = segment_words(word_binary)
    print(f"[INFO] Words detected: {len(word_boxes)}")
    
    if not word_boxes:
        return {
            "word_boxes": [],
            "word_images": [],
            "visualisation": original,
            "char_binary": char_binary,
            "word_binary": word_binary
        }
    
    # 3. Extract word images
    word_images = extract_word_images(original, word_boxes)
    
    # 4. Visualise
    vis = draw_word_boxes(original, word_boxes)
    
    return {
        "word_boxes": word_boxes,
        "word_images": word_images,
        "visualisation": vis,
        "char_binary": char_binary,
        "word_binary": word_binary
    }


def save_word_images(word_images, output_dir="test_images/words"):
    """Save individual word images for inspection."""
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    saved_paths = []
    for i, word_img in enumerate(word_images):
        path = os.path.join(output_dir, f"word_{i+1:02d}.png")
        cv2.imwrite(path, word_img)
        saved_paths.append(path)
    
    return saved_paths