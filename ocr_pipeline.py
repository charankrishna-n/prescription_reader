"""
ocr_pipeline.py
Full OCR pipeline:
  preprocess → segment → predict → form words/lines → clean
"""

import cv2
import numpy as np


# ─────────────────────────────────────────────
# PART 2 – IMAGE PREPROCESSING
# ─────────────────────────────────────────────

def _correct_lighting(gray):
    """Remove uneven lighting/shadows via CLAHE + background division."""
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    bg = cv2.GaussianBlur(enhanced, (51, 51), 0)
    norm = cv2.divide(enhanced, bg, scale=255)
    return norm


def _deskew(gray):
    """Correct small rotation via Hough line detection."""
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180,
                             threshold=80, minLineLength=50, maxLineGap=10)
    if lines is None:
        return gray

    angles = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        if x2 != x1:
            angles.append(np.degrees(np.arctan2(y2 - y1, x2 - x1)))

    if not angles:
        return gray

    median_angle = np.median(angles)
    if abs(median_angle) > 15:
        return gray

    h, w = gray.shape
    M = cv2.getRotationMatrix2D((w // 2, h // 2), median_angle, 1.0)
    return cv2.warpAffine(gray, M, (w, h),
                          flags=cv2.INTER_CUBIC,
                          borderMode=cv2.BORDER_REPLICATE)


def preprocess(image_path: str):
    """
    Load and preprocess a handwritten prescription photo.
    Returns (original_bgr, binary_image).
    binary_image: white ink on black background (EMNIST convention).
    """
    original = cv2.imread(image_path)
    if original is None:
        raise FileNotFoundError(f"Cannot open image: {image_path}")

    # Resize to 1000px wide — preserves detail from phone photos
    h, w = original.shape[:2]
    scale = 1000 / w
    original = cv2.resize(original, (1000, int(h * scale)))

    gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)

    # Fix uneven lighting from phone camera
    gray = _correct_lighting(gray)

    # Deskew if slightly tilted
    gray = _deskew(gray)

    # Gentle blur before thresholding
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)

    # Adaptive threshold → white ink on black background
    binary = cv2.adaptiveThreshold(
        blurred, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        blockSize=11, C=2
    )

    # Remove tiny specks
    kernel_open = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel_open)

    # Reconnect broken pen strokes
    kernel_dilate = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    binary = cv2.dilate(binary, kernel_dilate, iterations=1)

    return original, binary


# ─────────────────────────────────────────────
# PART 3 – CHARACTER SEGMENTATION
# ─────────────────────────────────────────────

def segment_characters(binary):
    """
    Detect contours and return (sorted_boxes, lines).
    sorted_boxes: flat list of (x,y,w,h) sorted line-by-line, left-to-right.
    lines: list of lines, each a list of (x,y,w,h).
    """
    contours, _ = cv2.findContours(
        binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    boxes = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        # FIXED: Stricter filtering for better character detection
        if w < 10 or h < 10:   # too small → noise
            continue
        if w > 100 or h > 100: # too large → merged text or artifacts
            continue
        if w > h * 3:          # too wide → likely merged characters
            continue
        if h > w * 3:          # too tall → likely merged lines
            continue
        boxes.append((x, y, w, h))

    if not boxes:
        return []

    LINE_TOLERANCE = 25

    boxes_sorted_y = sorted(boxes, key=lambda b: b[1])
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

    sorted_boxes = [box for line in lines for box in line]
    return sorted_boxes, lines


# ─────────────────────────────────────────────
# PART 4 – CHARACTER EXTRACTION + PREDICTION
# ─────────────────────────────────────────────

def _prepare_char(binary, box):
    """
    Crop a character from the binary image and prepare it for the model.
    CRITICAL: Must match EMNIST format exactly:
    - White text on black background
    - Character centered in 28x28 canvas
    - Proper aspect ratio preservation
    """
    x, y, w, h = box
    pad = 2
    x1 = max(0, x - pad)
    y1 = max(0, y - pad)
    x2 = min(binary.shape[1], x + w + pad)
    y2 = min(binary.shape[0], y + h + pad)

    char_img = binary[y1:y2, x1:x2]
    
    # Ensure we have a valid crop
    if char_img.size == 0 or char_img.shape[0] == 0 or char_img.shape[1] == 0:
        canvas = np.zeros((28, 28), dtype=np.float32)
        return canvas.reshape(1, 28, 28, 1)
    
    # Convert to grayscale if needed (should already be from binary)
    if len(char_img.shape) == 3:
        char_img = cv2.cvtColor(char_img, cv2.COLOR_BGR2GRAY)
    
    # Ensure uint8 type
    char_img = char_img.astype(np.uint8)
    
    # CRITICAL: Ensure WHITE text on BLACK background
    # binary image from THRESH_BINARY_INV should already be white-on-black
    # but double-check: if background is mostly white, invert
    if np.mean(char_img) > 127:
        char_img = cv2.bitwise_not(char_img)
    
    # CRITICAL: CENTER THE CHARACTER in 28x28 canvas
    # Preserve aspect ratio and center properly
    h_char, w_char = char_img.shape
    
    # Calculate scaling to fit in ~20x20 area (leave border for centering)
    max_dim = max(h_char, w_char)
    if max_dim > 20:
        scale = 20.0 / max_dim
        new_w = max(1, int(w_char * scale))
        new_h = max(1, int(h_char * scale))
        char_img = cv2.resize(char_img, (new_w, new_h), interpolation=cv2.INTER_AREA)
        h_char, w_char = new_h, new_w
    
    # Create blank 28x28 canvas (black background)
    canvas = np.zeros((28, 28), dtype=np.uint8)
    
    # Calculate position to center the character
    start_y = max(0, (28 - h_char) // 2)
    start_x = max(0, (28 - w_char) // 2)
    end_y = min(28, start_y + h_char)
    end_x = min(28, start_x + w_char)
    
    # Ensure we don't exceed canvas bounds
    crop_h = end_y - start_y
    crop_w = end_x - start_x
    
    # Place character in center of canvas
    canvas[start_y:end_y, start_x:end_x] = char_img[:crop_h, :crop_w]
    
    # Convert to float32 and normalize to [0, 1]
    canvas = canvas.astype(np.float32) / 255.0
    
    # Ensure correct shape and data type for TensorFlow
    result = canvas.reshape(1, 28, 28, 1)
    
    # Verify the result is valid
    if not np.isfinite(result).all():
        result = np.zeros((1, 28, 28, 1), dtype=np.float32)
    
    return result


def predict_character(model, label_map: dict, binary, box, debug=False):
    """Crop, prepare, predict one character. Returns (char, confidence)."""
    try:
        char_input = _prepare_char(binary, box)
        
        # Validate input shape and type
        if char_input.shape != (1, 28, 28, 1):
            print(f"[WARNING] Invalid input shape: {char_input.shape}, expected (1, 28, 28, 1)")
            return "?", 0.0
        
        if not np.isfinite(char_input).all():
            print(f"[WARNING] Invalid input data (NaN/Inf detected)")
            return "?", 0.0

        if debug:
            import matplotlib.pyplot as plt
            char_display = char_input.reshape(28, 28)
            plt.figure(figsize=(3, 3))
            plt.imshow(char_display, cmap="gray", vmin=0, vmax=1)
            plt.title(f"Input to model\nBox: {box}")
            plt.axis("off")
            plt.show()
            
            # Also print some stats about the character
            print(f"    Char stats: min={char_display.min():.3f}, max={char_display.max():.3f}, mean={char_display.mean():.3f}")
            print(f"    White pixels: {np.sum(char_display > 0.5)} / 784")

        prob = model.predict(char_input, verbose=0)
        label_idx = int(np.argmax(prob))
        confidence = float(np.max(prob))
        char = label_map.get(label_idx, "?")

        if debug:
            # Show top 3 predictions
            top3_idx = np.argsort(prob[0])[-3:][::-1]
            print(f"    Top 3: ", end="")
            for i, idx in enumerate(top3_idx):
                c = label_map.get(idx, "?")
                p = prob[0][idx]
                print(f"{c}({p:.3f})", end=" " if i < 2 else "\n")
            print(f"    FINAL: {char!r} (confidence: {confidence:.3f})")
            print()

        return char, confidence
        
    except Exception as e:
        print(f"[ERROR] Prediction failed for box {box}: {e}")
        return "?", 0.0


# ─────────────────────────────────────────────
# PART 5 – WORD / LINE FORMATION
# ─────────────────────────────────────────────

def form_text(lines: list, predictions: list) -> tuple:
    """
    Group predicted characters into words and lines.
    predictions: list of (char, confidence) tuples.
    Returns (raw_text, list_of_line_strings).
    """
    WORD_GAP_THRESHOLD = 30

    pred_iter = iter(predictions)
    text_lines = []

    for line_boxes in lines:
        words = []
        current_word = ""

        for i, box in enumerate(line_boxes):
            char, _ = next(pred_iter)
            current_word += char

            if i < len(line_boxes) - 1:
                next_box = line_boxes[i + 1]
                gap = next_box[0] - (box[0] + box[2])
                if gap > WORD_GAP_THRESHOLD:
                    words.append(current_word)
                    current_word = ""

        if current_word:
            words.append(current_word)

        text_lines.append(" ".join(words))

    return "\n".join(text_lines), text_lines


# ─────────────────────────────────────────────
# PART 8 – VISUALISATION
# ─────────────────────────────────────────────

def draw_boxes(original, boxes: list, predictions: list) -> np.ndarray:
    """Draw bounding boxes and predicted characters on the original image."""
    vis = original.copy()
    for (x, y, w, h), (char, conf) in zip(boxes, predictions):
        color = (0, 255, 0) if conf >= 0.5 else (0, 165, 255)  # green / orange
        cv2.rectangle(vis, (x, y), (x + w, y + h), color, 1)
        cv2.putText(vis, char, (x, y - 3),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45,
                    (0, 0, 255), 1, cv2.LINE_AA)
    return vis


# ─────────────────────────────────────────────
# MASTER PIPELINE FUNCTION
# ─────────────────────────────────────────────

def run_pipeline(image_path: str, model, label_map: dict,
                 debug: bool = False) -> dict:
    """
    End-to-end pipeline.
    Returns dict: raw_text, cleaned_text, visualisation, predictions.
    Set debug=True to show each character image and print confidence scores.
    """
    from utils import clean_text

    # 1. Preprocess
    original, binary = preprocess(image_path)

    # 2. Segment
    result = segment_characters(binary)
    if not result:
        return {"raw_text": "", "cleaned_text": "",
                "visualisation": original, "predictions": []}

    sorted_boxes, lines = result
    print(f"[INFO] Characters detected: {len(sorted_boxes)}")

    # 3. Predict each character
    predictions = []
    for i, box in enumerate(sorted_boxes):
        char, conf = predict_character(model, label_map, binary, box,
                                       debug=debug)
        predictions.append((char, conf))
        if debug:
            print(f"  [{i:03d}] char={char!r}  conf={conf:.3f}")

    # 4. Print confidence summary
    if predictions:
        avg_conf = np.mean([c for _, c in predictions])
        print(f"[INFO] Avg confidence: {avg_conf:.3f}")

    # 5. Form words / lines
    raw_text, _ = form_text(lines, predictions)

    # 6. Clean
    cleaned_text = clean_text(raw_text)

    # 7. Visualise
    vis = draw_boxes(original, sorted_boxes, predictions)

    return {
        "raw_text": raw_text,
        "cleaned_text": cleaned_text,
        "visualisation": vis,
        "predictions": predictions,
    }
