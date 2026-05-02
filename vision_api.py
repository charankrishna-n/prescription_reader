"""
vision_api.py
Google Cloud Vision API module for prescription text extraction.
Replaces EasyOCR with Google Vision's document_text_detection.

Credentials are loaded from environment variables for security.
"""

import os
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set Google credentials from environment variable
credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "key.json")
if not os.path.exists(credentials_path):
    raise FileNotFoundError(
        f"[ERROR] Google Cloud credentials file not found: '{credentials_path}'\n"
        "Please set GOOGLE_APPLICATION_CREDENTIALS in your .env file or ensure key.json exists."
    )

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

from google.cloud import vision
from google.api_core.exceptions import GoogleAPIError


def load_image_bytes(image_path: str) -> bytes:
    """
    Load image from disk and return its raw bytes.

    Args:
        image_path: Absolute or relative path to the image file.

    Returns:
        Raw bytes of the image.

    Raises:
        FileNotFoundError: If the image does not exist at the given path.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"[ERROR] Image file not found: '{image_path}'")

    with open(image_path, "rb") as f:
        return f.read()


def extract_text_from_image(image_path: str) -> str:
    """
    Extract raw text from a prescription image using Google Vision API
    (document_text_detection endpoint — optimised for dense, multi-line text).

    Args:
        image_path: Path to the prescription image (.jpg / .png / etc.)

    Returns:
        Extracted text as a plain string, or an empty string if none found.

    Raises:
        FileNotFoundError: If the image file does not exist.
        GoogleAPIError:    If the Vision API call fails.
    """
    # 1. Load image bytes
    image_bytes = load_image_bytes(image_path)

    # 2. Build Vision client + image object
    client = vision.ImageAnnotatorClient()
    image = vision.Image(content=image_bytes)

    # 3. Call document_text_detection (best for prescription / printed text)
    try:
        response = client.document_text_detection(image=image)
    except GoogleAPIError as api_err:
        raise GoogleAPIError(
            f"[ERROR] Google Vision API request failed: {api_err}"
        ) from api_err

    # 4. Check for API-level errors returned inside the response
    if response.error.message:
        raise GoogleAPIError(
            f"[ERROR] Vision API returned an error: {response.error.message}\n"
            "See: https://cloud.google.com/apis/design/errors"
        )

    # 5. Extract full text annotation
    full_text = response.full_text_annotation.text
    return full_text if full_text else ""


def extract_text_from_image_v2(image_path: str) -> str:
    """
    Extract raw text from a prescription image using a specified model
    version for potentially higher accuracy on messy documents.

    Args:
        image_path: Path to the prescription image.

    Returns:
        Extracted text as a plain string, or an empty string if none found.

    Raises:
        FileNotFoundError: If the image file does not exist.
        GoogleAPIError:    If the Vision API call fails.
    """
    image_bytes = load_image_bytes(image_path)

    client = vision.ImageAnnotatorClient()
    image = vision.Image(content=image_bytes)

    # Specify the model version to use. "builtin/latest" points to the
    # latest and most powerful model for text detection.
    features = [
        {"type_": vision.Feature.Type.TEXT_DETECTION, "model": "builtin/latest"}
    ]

    try:
        response = client.annotate_image(
            {"image": image, "features": features}
        )
    except GoogleAPIError as api_err:
        raise GoogleAPIError(
            f"[ERROR] Google Vision API request failed: {api_err}"
        ) from api_err

    if response.error.message:
        raise GoogleAPIError(
            f"[ERROR] Vision API returned an error: {response.error.message}"
        )

    # The response structure for annotate_image is slightly different
    if response.text_annotations:
        return response.text_annotations[0].description
    return ""


def clean_extracted_text(text: str) -> str:
    """
    Lightly clean the raw Vision API output:
    - Convert to lowercase
    - Collapse multiple whitespace / newlines into a single space
    - Strip leading/trailing whitespace

    Args:
        text: Raw text string from Vision API.

    Returns:
        Cleaned text string.
    """
    if not text:
        return ""

    text = text.lower()
    # Replace newlines and tabs with a space
    text = text.replace("\n", " ").replace("\t", " ")
    # Collapse multiple spaces
    text = re.sub(r" +", " ", text)
    return text.strip()


def get_prescription_text(image_path: str, clean: bool = True) -> str:
    """
    High-level helper: extract and optionally clean prescription text.

    Args:
        image_path: Path to the prescription image.
        clean:      If True (default), return cleaned lowercase text.
                    If False, return raw text as returned by the API.

    Returns:
        Extracted (and optionally cleaned) text string.
    """
    raw_text = extract_text_from_image(image_path)

    if clean:
        return clean_extracted_text(raw_text)
    return raw_text


if __name__ == "__main__":
    import sys

    test_image = sys.argv[1] if len(sys.argv) > 1 else None

    if not test_image:
        # Fall back to the first image in test_images/
        test_dir = "test_images"
        if os.path.isdir(test_dir):
            candidates = [
                f for f in os.listdir(test_dir)
                if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".tiff"))
            ]
            if candidates:
                test_image = os.path.join(test_dir, candidates[0])

    if not test_image:
        print("[ERROR] No test image found. Provide a path as an argument:")
        print("        python vision_api.py path/to/image.jpg")
        sys.exit(1)

    assert isinstance(test_image, str)
    print(f"[INFO] Running Vision API test on: {test_image}")
    print("-" * 50)

    try:
        # Using the new v2 function for extraction
        print("[INFO] Using new model-based text extraction (v2)...")
        text = get_prescription_text(test_image, clean=True)
        print("[SUCCESS] Extracted text:")
        print(text if text else "(no text detected)")

        # You can also compare with the old method if needed:
        # print("\n" + "-" * 50)
        # print("[INFO] Using original document text detection (v1)...")
        # text_v1 = clean_extracted_text(extract_text_from_image(test_image))
        # print("[SUCCESS] Extracted text (v1):")
        # print(text_v1 if text_v1 else "(no text detected)")

    except FileNotFoundError as e:
        print(e)
        sys.exit(1)
    except GoogleAPIError as e:
        print(e)
        sys.exit(1)
