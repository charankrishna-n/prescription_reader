"""
main.py
MediFill-like Prescription OCR System
Command-line interface for processing prescription images.

OCR backend: Google Cloud Vision API (document_text_detection)
"""

import sys
import os
import argparse
from prescription_pipeline import run_pipeline


def process_image(image_path: str, debug: bool = False) -> dict:
    """
    Process a single prescription image through the full pipeline.

    Args:
        image_path: Path to the image file
        debug: Show detailed processing information (passed through)

    Returns:
        Dict with parsed prescription data
    """
    return run_pipeline(image_path, verbose=True)


def main():
    """Main command-line interface."""
    parser = argparse.ArgumentParser(
        description="MediFill-like Prescription OCR System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                          # Process first image in test_images/
  python main.py prescription.jpg         # Process specific image
  python main.py prescription.jpg --debug # Show detailed processing info
        """
    )

    parser.add_argument(
        'image_path',
        nargs='?',
        help='Path to prescription image (optional - uses first image in test_images/)'
    )

    parser.add_argument(
        '--debug', '-d',
        action='store_true',
        help='Show detailed processing information'
    )

    args = parser.parse_args()

    # Determine image path
    if args.image_path:
        image_path = args.image_path
    else:
        # Use first image from test_images directory
        test_dir = "test_images"
        if not os.path.exists(test_dir):
            print(f"[ERROR] test_images directory not found.")
            sys.exit(1)

        images = [
            f for f in os.listdir(test_dir)
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff'))
            and not f.startswith('output_')  # Skip output files
        ]

        if not images:
            print(f"[ERROR] No images found in {test_dir}/")
            print("Please add prescription images to the test_images directory.")
            sys.exit(1)

        image_path = os.path.join(test_dir, images[0])
        print(f"[INFO] Using default image: {images[0]}")

    # Validate image exists
    if not os.path.exists(image_path):
        print(f"[ERROR] Image not found: {image_path}")
        sys.exit(1)

    # Process the image
    result = process_image(image_path, debug=args.debug)

    if "error" in result:
        sys.exit(1)


if __name__ == "__main__":
    main()
