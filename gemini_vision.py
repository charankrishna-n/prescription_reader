"""
gemini_vision.py
Gemini image understanding for prescription extraction.
"""

import json
import mimetypes
import os
from typing import Any, Dict, List

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

DEFAULT_GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def _guess_mime_type(image_path: str) -> str:
    mime, _ = mimetypes.guess_type(image_path)
    return mime or "image/png"


def _strip_json_fence(text: str) -> str:
    if not text:
        return ""
    content = text.strip()
    if content.startswith("```"):
        lines = content.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        content = "\n".join(lines).strip()
    return content


def _normalise_medicine_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    normalised = []
    for row in rows or []:
        normalised.append(
            {
                "medicine": str(row.get("medicine", "Unknown") or "Unknown").strip(),
                "quantity": str(row.get("quantity", "N/A") or "N/A").strip(),
                "when_to_take": str(row.get("when_to_take", "N/A") or "N/A").strip(),
                "duration": str(row.get("duration", "N/A") or "N/A").strip(),
                "dosage": str(row.get("dosage", "N/A") or "N/A").strip(),
                "meal_context": str(row.get("meal_context", "N/A") or "N/A").strip(),
                "confidence": float(row.get("confidence", 0.7) or 0.7),
            }
        )
    return normalised


def extract_prescription_with_gemini(image_path: str) -> Dict[str, Any]:
    """
    Read prescription image and return structured medicine details.

    Returns:
        {
          "raw_text": str,
          "parsed_medicines": [
              {
                "medicine": str,
                "quantity": str,
                "when_to_take": str,
                "duration": str,
                "dosage": str,
                "meal_context": str,
                "confidence": float
              }
          ]
        }
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing in .env")

    client = genai.Client(api_key=api_key)

    with open(image_path, "rb") as f:
        image_bytes = f.read()

    prompt = (
        "You are a medical prescription reader. "
        "Extract medicine schedule information from the attached prescription image. "
        "Return strict JSON with this schema: "
        "{\"raw_text\": string, \"medicines\": [{\"medicine\": string, \"quantity\": string, "
        "\"when_to_take\": string, \"duration\": string, \"dosage\": string, "
        "\"meal_context\": string, \"confidence\": number}]}. "
        "Rules: "
        "1) Keep unavailable fields as \"N/A\". "
        "2) For dosage, prefer compact format like 1-0-1 if inferable else N/A. "
        "3) raw_text should be OCR-style plain text of the prescription. "
        "4) Do not include markdown, code fences, or extra keys."
    )

    response = client.models.generate_content(
        model=DEFAULT_GEMINI_MODEL,
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type=_guess_mime_type(image_path)),
            prompt,
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.1,
        ),
    )

    text = _strip_json_fence(response.text or "")
    payload = json.loads(text)

    return {
        "raw_text": str(payload.get("raw_text", "") or ""),
        "parsed_medicines": _normalise_medicine_rows(payload.get("medicines", [])),
    }
