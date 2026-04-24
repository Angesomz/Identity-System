"""
id_extractor.py
---------------
Core OCR + AI extraction engine for identity documents.

Pipeline:
1. Decode base64 image → OpenCV ndarray
2. Pre-process (denoise, greyscale, adaptive threshold) for better OCR
3. Run EasyOCR to get raw text
4. If GEMINI_API_KEY is set → send text through LLM prompt for smart field extraction
5. Otherwise run regex-based fayda_parser (offline fallback)
6. Return structured OCRResult dataclass
"""
import base64
import json
import logging
import os
import re
import traceback
from dataclasses import dataclass, field
from typing import Optional

import cv2
import numpy as np

from .fayda_parser import parse_fields

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------ #
#  OCR_PROMPT – mirrors the prompt from the user's specification      #
# ------------------------------------------------------------------ #

OCR_PROMPT_TEMPLATE = """You are an expert in identity document recognition, specializing in Ethiopian Fayda National ID cards.

The following text was extracted using OCR and may contain noise.

Your task:
1. Identify key identity fields
2. Correct OCR errors intelligently  
3. Return ONLY valid JSON – no markdown, no explanation

Fields to extract:
- full_name        (string or null)
- id_number        (string or null, Ethiopian format like ET-XXXX-XXXX)
- date_of_birth    (string or null, format DD/MM/YYYY if possible)
- nationality      (string or null, default "Ethiopian" if document is Ethiopian)
- sex              (string or null, "M" or "F")
- document_type    (string or null, e.g. "National ID", "Fayda ID")
- confidence_score (float 0.0–1.0, your overall confidence in the extraction)

OCR TEXT:
\"\"\"
{ocr_text}
\"\"\"

Return ONLY a JSON object like:
{{
  "full_name": "...",
  "id_number": "...",
  "date_of_birth": "...",
  "nationality": "...",
  "sex": "...",
  "document_type": "...",
  "confidence_score": 0.85
}}"""


@dataclass
class OCRResult:
    full_name: Optional[str] = None
    id_number: Optional[str] = None
    date_of_birth: Optional[str] = None
    nationality: Optional[str] = None
    sex: Optional[str] = None
    document_type: Optional[str] = None
    confidence_score: float = 0.0
    raw_ocr_text: str = ""
    extraction_method: str = "regex"   # "regex" | "llm"


class IDExtractor:
    """
    Singleton-safe OCR extraction engine.
    EasyOCR reader is lazy-loaded on first call to avoid blocking app startup.
    """

    def __init__(self):
        self._reader = None
        # Prefer reading from pydantic Settings (loads .env correctly),
        # fall back to os.environ for flexibility.
        try:
            from configs.settings import get_settings
            _settings = get_settings()
            self._gemini_key = (_settings.GEMINI_API_KEY or "").strip()
        except Exception:
            self._gemini_key = os.environ.get("GEMINI_API_KEY", "").strip()

        self._gemini_model = None
        if self._gemini_key:
            self._init_gemini()

    # ---------------------------------------------------------------- #
    #  Initialisation helpers                                            #
    # ---------------------------------------------------------------- #

    def _init_gemini(self):
        try:
            import google.generativeai as genai
            genai.configure(api_key=self._gemini_key)
            self._gemini_model = genai.GenerativeModel("gemini-1.5-flash")
            logger.info("[IDExtractor] Gemini LLM initialised successfully.")
        except Exception as e:
            logger.warning(f"[IDExtractor] Gemini init failed: {e}. Falling back to regex.")
            self._gemini_model = None

    def _get_reader(self):
        """Lazy-load EasyOCR reader (downloads weights on first call)."""
        if self._reader is None:
            try:
                import easyocr
                # Support English (en) and Amharic (am) for Fayda IDs
                # Note: 'am' is Amharic — falls back to 'en' only if not available
                try:
                    self._reader = easyocr.Reader(["en", "am"], gpu=True, verbose=False)
                    logger.info("[IDExtractor] EasyOCR reader loaded with en+am.")
                except Exception:
                    self._reader = easyocr.Reader(["en"], gpu=True, verbose=False)
                    logger.info("[IDExtractor] EasyOCR reader loaded with en only.")
            except ImportError:
                raise RuntimeError(
                    "EasyOCR is not installed. Run: pip install easyocr"
                )
        return self._reader

    # ---------------------------------------------------------------- #
    #  Image preprocessing                                               #
    # ---------------------------------------------------------------- #

    @staticmethod
    def _preprocess(image: np.ndarray) -> np.ndarray:
        """
        Convert to greyscale, apply CLAHE contrast enhancement,
        and adaptive threshold to make OCR more robust.
        """
        if image is None:
            raise ValueError("Image is None — cannot preprocess.")
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # CLAHE – adaptive histogram equalisation for contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        # Bilateral filter – preserves edges while reducing noise
        denoised = cv2.bilateralFilter(enhanced, 9, 75, 75)
        # Adaptive thresholding for better binarisation
        thresh = cv2.adaptiveThreshold(
            denoised, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        return thresh

    # ---------------------------------------------------------------- #
    #  OCR                                                               #
    # ---------------------------------------------------------------- #

    def _run_ocr(self, image: np.ndarray) -> str:
        """Run EasyOCR and return the joined text."""
        reader = self._get_reader()
        
        # Optimize size for OCR speed
        h, w = image.shape[:2]
        if w > 1024:
            scale = 1024 / w
            image = cv2.resize(image, (int(w * scale), int(h * scale)))

        preprocessed = self._preprocess(image)
        # Avoid double-running (originally ran on both raw AND preprocessed). 
        # Running once on preprocessed text is typically better & cuts execution time in HALF.
        results_proc = reader.readtext(preprocessed, detail=0, paragraph=False)

        # Merge: unique lines, preserve order
        seen = set()
        merged = []
        for line in results_proc:
            key = line.strip().lower()
            if key and key not in seen:
                seen.add(key)
                merged.append(line.strip())

        raw_text = "\n".join(merged)
        logger.debug(f"[IDExtractor] Raw OCR text:\n{raw_text}")
        return raw_text

    # ---------------------------------------------------------------- #
    #  LLM-based extraction                                              #
    # ---------------------------------------------------------------- #

    def _extract_with_llm(self, ocr_text: str) -> Optional[dict]:
        """Send OCR text to Gemini and parse JSON response."""
        if not self._gemini_model:
            return None
        try:
            prompt = OCR_PROMPT_TEMPLATE.format(ocr_text=ocr_text)
            response = self._gemini_model.generate_content(prompt)
            raw = response.text.strip()
            # Strip markdown code fences if present
            raw = re.sub(r"^```[a-z]*\n?", "", raw, flags=re.MULTILINE)
            raw = re.sub(r"```$", "", raw.strip())
            data = json.loads(raw)
            logger.info("[IDExtractor] Gemini extraction succeeded.")
            return data
        except Exception as e:
            logger.warning(f"[IDExtractor] Gemini extraction failed: {e}. Falling back to regex.")
            return None

    # ---------------------------------------------------------------- #
    #  Public API                                                        #
    # ---------------------------------------------------------------- #

    def extract(self, image: np.ndarray) -> OCRResult:
        """
        Full pipeline: preprocess → OCR → LLM or regex extraction.
        Always returns an OCRResult, never raises.
        """
        raw_ocr_text = ""
        try:
            raw_ocr_text = self._run_ocr(image)
        except Exception as e:
            logger.error(f"[IDExtractor] OCR failed: {e}\n{traceback.format_exc()}")
            return OCRResult(raw_ocr_text="", confidence_score=0.0)

        # Try LLM first
        data = self._extract_with_llm(raw_ocr_text)
        method = "llm"

        # Fall back to regex parser
        if data is None:
            data = parse_fields(raw_ocr_text)
            method = "regex"

        # Sanitise — ensure all expected keys are present
        def _s(key: str) -> Optional[str]:
            v = data.get(key)
            return str(v).strip() if v and str(v).strip().lower() not in ("null", "none", "") else None

        return OCRResult(
            full_name=_s("full_name"),
            id_number=_s("id_number"),
            date_of_birth=_s("date_of_birth"),
            nationality=_s("nationality") or "Ethiopian",
            sex=_s("sex"),
            document_type=_s("document_type") or "National ID",
            confidence_score=float(data.get("confidence_score") or 0.0),
            raw_ocr_text=raw_ocr_text,
            extraction_method=method,
        )

    def extract_from_base64(self, b64_string: str) -> OCRResult:
        """Convenience wrapper: decode base64 → extract."""
        try:
            if "," in b64_string:
                b64_string = b64_string.split(",")[1]
            decoded = base64.b64decode(b64_string)
            np_arr = np.frombuffer(decoded, np.uint8)
            image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            if image is None:
                raise ValueError("Could not decode image from base64.")
            return self.extract(image)
        except Exception as e:
            logger.error(f"[IDExtractor] base64 decode failed: {e}")
            return OCRResult(raw_ocr_text="", confidence_score=0.0)
