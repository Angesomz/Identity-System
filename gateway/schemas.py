from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional
from datetime import datetime
from uuid import UUID

class BaseResponse(BaseModel):
    success: bool
    message: str = "Operation successful"
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class EnrollmentRequest(BaseModel):
    national_id: str = Field(..., description="Unique National ID")
    full_name: str
    image_base64: str = Field(..., description="Base64 encoded face image")
    metadata: Optional[dict] = {}

class SearchRequest(BaseModel):
    image_base64: str
    top_k: int = 5
    threshold: Optional[float] = None

class VerifyRequest(BaseModel):
    national_id: str
    image_base64: str

class IdentityMatch(BaseModel):
    national_id: str
    score: float
    confidence: str
    metadata: Optional[dict]

class SearchResponse(BaseResponse):
    matches: List[IdentityMatch]
    count: int

class EnrollmentResponse(BaseResponse):
    enrollment_id: str

class IdentitySchema(BaseModel):
    id: int
    national_id: str
    full_name: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class IdentityListResponse(BaseResponse):
    identities: List[IdentitySchema]
    count: int


# ---------------------------------------------------------------------------
# OCR / Document Scanning
# ---------------------------------------------------------------------------

class OCRScanRequest(BaseModel):
    """Request body for the /ocr/scan-id endpoint."""
    image_base64: str = Field(..., description="Base64-encoded image of the identity document")


class OCRScanResponse(BaseResponse):
    """Structured identity fields extracted from an ID document via OCR."""
    full_name: Optional[str] = None
    id_number: Optional[str] = None
    date_of_birth: Optional[str] = None
    nationality: Optional[str] = None
    sex: Optional[str] = None
    document_type: Optional[str] = None
    confidence_score: float = 0.0
    raw_ocr_text: str = ""
    extraction_method: str = "regex"  # "regex" | "llm"
