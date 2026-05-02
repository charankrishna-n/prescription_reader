"""
ocr_engine.py
OCR Engine using EasyOCR for text extraction from prescription images.
"""

import cv2
import numpy as np
import os
import re
from difflib import get_close_matches
import easyocr


class OCREngine:
    def __init__(self, lang_list=['en']):
        """
        Initialize EasyOCR reader.
        lang_list: List of languages to recognize (default: English)
        """
        self.reader = easyocr.Reader(lang_list)

    def preprocess_image(self, image_path):
        """
        Preprocess image for better OCR results.
        - Resize for optimal OCR performance
        - Enhance contrast using CLAHE
        - Convert to grayscale
        - Apply bilateral filter to reduce noise while preserving edges
        """
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError(f"Cannot load image: {image_path}")

        # Resize to optimal size for OCR (maintain aspect ratio)
        height, width = image.shape[:2]
        max_dimension = 2000
        if max(height, width) > max_dimension:
            scale = max_dimension / max(height, width)
            new_width = int(width * scale)
            new_height = int(height * scale)
            image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
        elif max(height, width) < 500:
            # Upscale small images for better OCR
            scale = 500 / min(height, width)
            new_width = int(width * scale)
            new_height = int(height * scale)
            image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_CUBIC)

        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply bilateral filter to reduce noise while preserving edges
        denoised = cv2.bilateralFilter(gray, 9, 75, 75)

        # Enhance contrast using CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)

        return enhanced

    def extract_text(self, image_path):
        """
        Extract text from prescription image using EasyOCR.

        Args:
            image_path: Path to the image file

        Returns:
            Raw extracted text as string
        """
        # Preprocess image
        processed_image = self.preprocess_image(image_path)

        # Run EasyOCR
        result = self.reader.readtext(processed_image)

        # Extract text
        text = " ".join([res[1] for res in result])

        return text

    def clean_text(self, text: str) -> str:
        """
        Clean OCR text:
        - Convert to lowercase
        - Remove special characters except alphanumeric, spaces, and hyphens
        - Remove extra spaces
        """
        if not text:
            return ""

        # Convert to lowercase
        text = text.lower()

        # Remove unwanted symbols (keep letters, numbers, spaces, hyphens for dosage)
        text = re.sub(r'[^a-z0-9\s\-]', '', text)

        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    def match_medicines(self, text: str) -> str:
        """
        Match words with medicine list and extract medicine names with similarity > 0.6
        """
        # Medicine list (can be expanded)
        medicine_list = [
            "augmentin", "enzoflam", "pantoprazole", "hexigel", "paracetamol",
            "amoxicillin", "metformin", "atorvastatin", "omeprazole", "cetirizine",
            "azithromycin", "ibuprofen", "aspirin", "metronidazole", "ciprofloxacin",
            "diclofenac", "ranitidine", "losartan", "amlodipine", "hydrochlorothiazide",
            "prednisone", "warfarin", "insulin", "levothyroxine", "simvastatin"
        ]

        words = text.split()
        extracted_medicines = []

        for word in words:
            # Skip very short words
            if len(word) < 3:
                continue
            
            # Find close matches with cutoff of 0.6
            matches = get_close_matches(word, medicine_list, n=1, cutoff=0.6)
            if matches:
                extracted_medicines.append(matches[0])  # Add matched medicine

        # Remove duplicates while preserving order
        seen = set()
        unique_medicines = []
        for med in extracted_medicines:
            if med not in seen:
                seen.add(med)
                unique_medicines.append(med)

        return " ".join(unique_medicines) if unique_medicines else "(no medicines detected)"

    def get_text_with_confidence(self, image_path):
        """
        Extract text with confidence scores.

        Returns:
            Tuple: (raw_text, cleaned_text, extracted_medicines)
        """
        # Get raw OCR text
        raw_text = self.extract_text(image_path)

        # Clean text
        cleaned_text = self.clean_text(raw_text)

        # Match medicines
        extracted_medicines = self.match_medicines(cleaned_text)

        return raw_text, cleaned_text, extracted_medicines


def test_ocr_engine():
    """Test function for OCR engine."""
    engine = OCREngine()

    # Test with first image in test_images directory
    test_dir = "test_images"
    if os.path.exists(test_dir):
        images = [f for f in os.listdir(test_dir)
                 if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]

        if images:
            test_image = os.path.join(test_dir, images[0])
            print(f"Testing OCR on: {test_image}")

            raw_text, cleaned_text, extracted_medicines = engine.get_text_with_confidence(test_image)
            print(f"Raw Text: {raw_text}")
            print(f"Cleaned Text: {cleaned_text}")
            print(f"Extracted Medicines: {extracted_medicines}")


if __name__ == "__main__":
    test_ocr_engine()