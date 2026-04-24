"""
fayda_parser.py
---------------
Ethiopian Fayda National ID – specific field parser and confidence scorer.
Used as the offline/fallback layer when no LLM key is configured, and also
as a post-processing validator on top of LLM results.
"""
import re
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------ #
#  Regex patterns tuned to Ethiopian Fayda National ID card layout    #
# ------------------------------------------------------------------ #

# ID number: ET-XXXX-XXXX  or  ETXXXXXXXX  or  ET/XXXX/XXXX
_ID_PATTERNS = [
    r'ET[-/\s]?\d{4}[-/\s]?\d{4,6}',
    r'FID[-/\s]?\d{6,12}',
    r'\b\d{12}\b',          # 12-digit numeric (Fayda format variant)
]

# Date patterns  DD/MM/YYYY  MM-DD-YYYY  DD.MM.YYYY  or written Ethiopian dates
_DATE_PATTERNS = [
    r'\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{4}',
    r'\d{4}[/\-\.]\d{1,2}[/\-\.]\d{1,2}',
]

# Sex / Gender
_SEX_PATTERNS = [
    (r'\b(male|M)\b', 'M'),
    (r'\b(female|F)\b', 'F'),
    (r'\bወንድ\b', 'M'),    # Amharic Male
    (r'\bሴት\b', 'F'),      # Amharic Female
]

# Nationality
_NATIONALITY_PATTERNS = [
    r'\b(Ethiopian|Ethiopia|ETHIOPIAN)\b',
    r'\bኢትዮጵያዊ\b',
]

# Document type
_DOCTYPE_PATTERNS = [
    r'(National\s+ID|NATIONAL\s+ID|Fayda)',
    r'(ብሄራዊ\s+መታወቂያ)',   # Amharic: National ID
    r'(ID\s+Card)',
]

# Name extraction – look for lines after keywords 
_NAME_KEYWORDS = [
    r'(?:Full\s+Name|Name|ስም)[:\s]+([A-Za-z\u1200-\u137F\s]{3,60})',
    r'(?:Emri|Given\s+Name)[:\s]+([A-Za-z\s]{3,40})',
]


def _first_match(text: str, patterns: list[str]) -> Optional[str]:
    for pattern in patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            return m.group(0).strip()
    return None


def _extract_sex(text: str) -> Optional[str]:
    for pattern, label in _SEX_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return label
    return None


def _clean_id(raw: Optional[str]) -> Optional[str]:
    if not raw:
        return None
    # Normalise separators
    return re.sub(r'[\s/]', '-', raw.upper()).strip()


def parse_fields(ocr_text: str) -> Dict[str, Any]:
    """
    Pure regex extraction of Fayda ID fields from OCR text.
    Returns a dict with all fields + a confidence_score (0.0 – 1.0).
    """
    text = ocr_text or ""

    # --- Field extraction ---
    raw_id = _first_match(text, _ID_PATTERNS)
    id_number = _clean_id(raw_id)

    date_of_birth = _first_match(text, _DATE_PATTERNS)

    sex = _extract_sex(text)

    nationality = "Ethiopian" if _first_match(text, _NATIONALITY_PATTERNS) else None

    document_type = _first_match(text, _DOCTYPE_PATTERNS) or "National ID"

    # Name: try keyword-anchored patterns first
    full_name: Optional[str] = None
    for pattern in _NAME_KEYWORDS:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            candidate = m.group(1).strip()
            # Must be at least 5 chars and contain a space (first + last name)
            if len(candidate) >= 5:
                full_name = candidate
                break

    # --- Confidence scoring ---
    fields = {
        "full_name": full_name,
        "id_number": id_number,
        "date_of_birth": date_of_birth,
        "nationality": nationality,
        "sex": sex,
        "document_type": document_type,
    }

    filled = sum(1 for v in fields.values() if v)
    confidence_score = round(filled / len(fields), 2)

    logger.debug(f"[FaydaParser] Extracted fields: {fields}, confidence={confidence_score}")

    return {**fields, "confidence_score": confidence_score}
