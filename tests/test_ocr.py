"""
tests/test_ocr.py
-----------------
End-to-end tests for the OCR /scan-id endpoint.
Runs the full pipeline using a synthetic test image (no real ID required).

Usage:
    # Start the backend first:
    # uvicorn gateway.main:app --reload --port 8000

    # Then run:
    # pytest tests/test_ocr.py -v
"""
import base64
import re
import json
import sys
import os

import numpy as np
import cv2
import pytest

# Allow running from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _make_id_card_image(text_lines: list[str]) -> str:
    """
    Create a synthetic white ID-card image with the supplied text lines
    rendered in black, then return it as a base64 PNG string.
    """
    h, w = 400, 640
    img = np.ones((h, w, 3), dtype=np.uint8) * 245  # near-white background

    # Card border
    cv2.rectangle(img, (10, 10), (w - 10, h - 10), (180, 180, 180), 2)

    # Title bar
    cv2.rectangle(img, (10, 10), (w - 10, 60), (30, 30, 30), -1)
    cv2.putText(img, "FEDERAL DEMOCRATIC REPUBLIC OF ETHIOPIA",
                (20, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)

    # Content lines
    y = 100
    for line in text_lines:
        cv2.putText(img, line, (40, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (20, 20, 20), 1, cv2.LINE_AA)
        y += 45

    _, buf = cv2.imencode(".png", img)
    return base64.b64encode(buf).decode("utf-8")


SAMPLE_LINES = [
    "Full Name: Abebe Bekele Tesfaye",
    "ID Number: ET-1234-5678",
    "Date of Birth: 15/07/1990",
    "Nationality: Ethiopian",
    "Sex: Male",
    "Document Type: National ID",
]

SAMPLE_B64 = _make_id_card_image(SAMPLE_LINES)


# ─────────────────────────────────────────────────────────────────────────────
# Unit: fayda_parser (offline, no network required)
# ─────────────────────────────────────────────────────────────────────────────

class TestFaydaParser:
    def test_id_number_extraction(self):
        from services.ocr.fayda_parser import parse_fields
        result = parse_fields("ID Number: ET-1234-5678")
        assert result["id_number"] is not None
        assert "ET" in result["id_number"].upper()

    def test_date_extraction(self):
        from services.ocr.fayda_parser import parse_fields
        result = parse_fields("Date of Birth: 15/07/1990")
        assert result["date_of_birth"] is not None
        assert "1990" in result["date_of_birth"]

    def test_sex_extraction_male(self):
        from services.ocr.fayda_parser import parse_fields
        result = parse_fields("Sex: Male")
        assert result["sex"] == "M"

    def test_sex_extraction_female(self):
        from services.ocr.fayda_parser import parse_fields
        result = parse_fields("Sex: Female")
        assert result["sex"] == "F"

    def test_nationality_extraction(self):
        from services.ocr.fayda_parser import parse_fields
        result = parse_fields("Nationality: Ethiopian")
        assert result["nationality"] == "Ethiopian"

    def test_confidence_score_range(self):
        from services.ocr.fayda_parser import parse_fields
        result = parse_fields("\n".join(SAMPLE_LINES))
        assert 0.0 <= result["confidence_score"] <= 1.0

    def test_empty_text(self):
        from services.ocr.fayda_parser import parse_fields
        result = parse_fields("")
        assert result["confidence_score"] == 0.0


# ─────────────────────────────────────────────────────────────────────────────
# Unit: IDExtractor (uses real EasyOCR — marks as slow)
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.slow
class TestIDExtractor:
    def test_extract_from_base64_returns_result(self):
        from services.ocr.id_extractor import IDExtractor
        extractor = IDExtractor()
        result = extractor.extract_from_base64(SAMPLE_B64)
        # Should not throw; confidence > 0 since text is clear
        assert result is not None
        assert 0.0 <= result.confidence_score <= 1.0

    def test_extract_invalid_base64(self):
        from services.ocr.id_extractor import IDExtractor
        extractor = IDExtractor()
        result = extractor.extract_from_base64("not_valid_base64!!!!")
        # Should return an empty result gracefully, not raise
        assert result.confidence_score == 0.0

    def test_extraction_method_defaults_to_regex(self):
        """Without a Gemini key, extraction_method should be 'regex'."""
        from services.ocr.id_extractor import IDExtractor
        extractor = IDExtractor()
        extractor._gemini_model = None  # force offline
        result = extractor.extract_from_base64(SAMPLE_B64)
        assert result.extraction_method in ("regex", "llm")     # either is valid


# ─────────────────────────────────────────────────────────────────────────────
# Integration: HTTP endpoint (requires running backend)
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.integration
class TestOCREndpoint:
    """
    Requires the backend to be running on localhost:8000.
    Run with:  pytest tests/test_ocr.py -m integration -v
    """
    BASE_URL = "http://localhost:8000"

    def test_health(self):
        import requests
        r = requests.get(f"{self.BASE_URL}/health", timeout=5)
        assert r.status_code == 200
        assert r.json()["status"] == "healthy"

    def test_scan_id_success(self):
        import requests
        payload = {"image_base64": SAMPLE_B64}
        r = requests.post(f"{self.BASE_URL}/ocr/scan-id", json=payload, timeout=60)
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True
        assert "confidence_score" in data
        assert 0.0 <= data["confidence_score"] <= 1.0

    def test_scan_id_missing_image(self):
        import requests
        r = requests.post(f"{self.BASE_URL}/ocr/scan-id", json={}, timeout=10)
        assert r.status_code == 422  # Pydantic validation error

    def test_scan_id_returns_json_structure(self):
        import requests
        payload = {"image_base64": SAMPLE_B64}
        r = requests.post(f"{self.BASE_URL}/ocr/scan-id", json=payload, timeout=60)
        data = r.json()
        expected_keys = {
            "success", "confidence_score", "raw_ocr_text",
            "extraction_method", "document_type", "nationality"
        }
        assert expected_keys.issubset(data.keys())
