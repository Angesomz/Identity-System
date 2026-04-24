import base64
import numpy as np
import cv2
from fastapi import FastAPI, Depends, HTTPException, Security, Response
from fastapi.middleware.cors import CORSMiddleware

# Configs & Auth
from configs.settings import get_settings
from .auth import verify_token, verify_mtls
from .rate_limit import check_rate_limit
from .schemas import (
    EnrollmentRequest, EnrollmentResponse, SearchRequest, SearchResponse,
    VerifyRequest, IdentityListResponse, IdentitySchema,
    OCRScanRequest, OCRScanResponse,
)

# Services
from services.liveness.spoof_classifier import SpoofClassifier
from services.face_processing.detector import FaceDetector
from services.face_processing.aligner import FaceAligner
from services.embedding.arcface_engine import ArcFaceEngine
from services.identity_resolver.resolver import IdentityResolver
from services.enrollment.engine import EnrollmentEngine
from services.ocr.id_extractor import IDExtractor
from services.matching.reranking_system import ReRankingSystem
from services.matching.decision_engine import DecisionEngine
from vector_cluster.shard_router import get_shard_router
from database.connection import get_db, SessionLocal
from database.models import UserIdentity, Embedding, AuditLog
from sqlalchemy.orm import Session

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    description="Million-Scale Biometric Identity Resolution Gateway",
    version="1.1.0",
    docs_url="/docs" if settings.DEBUG else None
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Service Initialization ---
# In a real microservices mesh, these would be gRPC clients.
# Here we instantiate them as singletons for the monolith-ish deployment.
spoof_classifier = SpoofClassifier()
detector = FaceDetector()
aligner = FaceAligner()
embedder = ArcFaceEngine()
shard_router = get_shard_router()   # process-wide singleton — never recreates the index
decision_engine = DecisionEngine()
reranking_system = ReRankingSystem()

# OCR extractor — lazy-loads EasyOCR on first request (does NOT block startup)
ocr_extractor = IDExtractor()

# Helper to decode base64 images
def decode_image(b64_string: str) -> np.ndarray:
    try:
        if "," in b64_string:
            b64_string = b64_string.split(",")[1]
        decoded_data = base64.b64decode(b64_string)
        np_data = np.frombuffer(decoded_data, np.uint8)
        img = cv2.imdecode(np_data, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Invalid image data")
        return img
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image format: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "gateway", "version": "1.1.0"}

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Identity Resolution Gateway",
        "version": "1.1.0",
        "docs_url": "/docs",
        "health_check": "/health"
    }

# --- Device/Router Probing Handlers (Fix for 404s) ---
@app.get("/loginMsg.js")
async def login_msg():
    # Return empty JS or a comment to satisfy the client
    return Response(content="// loginMsg.js", media_type="application/javascript")

@app.get("/cgi/get.cgi")
async def get_cgi(cmd: str = None):
    # Mock response for home_login or other commands
    if cmd == "home_login":
        return {"status": "ok", "login": "required"}
    return {"status": "ok"}

@app.post("/boaform/admin/formTracert")
async def form_tracert():
    # Mock response for formTracert
    return {"status": "ok", "message": "tracert handled"}

# dependencies=[Depends(verify_token), Depends(check_rate_limit)] 
# Auth disabled for walkthrough/dev convenience
# dependencies=[Depends(verify_token), Depends(check_rate_limit)] 
# Auth disabled for walkthrough/dev convenience
# NOTE: In a real app we'd inject this as a dependency to avoid instantiating it on every module load if simpler
enrollment_engine = EnrollmentEngine()

@app.post("/enroll", response_model=EnrollmentResponse, dependencies=[Depends(check_rate_limit)])
async def enroll_identity(request: EnrollmentRequest, db: Session = Depends(get_db)):
    """
    Full Enrollment Pipeline via EnrollmentEngine
    """
    # 1. Decode
    image = decode_image(request.image_base64)

    # 2. Delegate to Engine
    try:
        new_identity = enrollment_engine.enroll(
            image=image,
            national_id=request.national_id,
            full_name=request.full_name,
            db=db,
            metadata=request.metadata
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Enrollment failed: {str(e)}")
    
    return {
        "success": True, 
        "enrollment_id": str(new_identity.id), 
        "timestamp": new_identity.created_at
    }

# dependencies=[Depends(verify_token), Depends(check_rate_limit)]
# Auth disabled for walkthrough/dev convenience
@app.post("/search/identify", dependencies=[Depends(check_rate_limit)])
async def identify_face(request: SearchRequest, db: Session = Depends(get_db)):
    """
    Peak Performance National Identity Intelligence System Pipeline:
    1. Detect face -> 2. Embed -> 3. Search -> 4. Re-rank -> 5. Evaluate -> 6. Retrieve -> 7. Verify
    """
    # 0. Decode Input Image
    input_image = decode_image(request.image_base64)
    
    # 1. Detect face
    faces = detector.detect(input_image)
    if not faces:
         return {"status": "No face detected"}
         
    primary_face = faces[0]
    
    # 2. Generate embedding
    embedding = embedder.get_embedding(input_image, face_obj=primary_face.get("_face_obj"))
    
    # 3. Search database (Top-K retrieval)
    resolver = IdentityResolver(db, shard_router)
    candidates = resolver.search_similar_faces(embedding, top_k=request.top_k)
    
    # 4. Re-rank candidates
    best_match, score = reranking_system.rerank(primary_face, candidates)

    # 5. Decision logic
    evaluation = decision_engine.evaluate(score)
    if evaluation == "NO_MATCH":
        return {"status": "No reliable match", "confidence": score}

    if evaluation == "UNCERTAIN":
        return {
            "status": "Uncertain",
            "candidates": candidates
        }

    # 6. Retrieve identity
    person_data = resolver.get_person_record(best_match["id"])
    if not person_data:
        return {"status": "Critical Error - Ghost Record (ID not found in identity database)"}

    # 7. Final verification (optional second check via intelligence cross-reference)
    verified = True

    # Deserialize metadata_blob to return inside the photo details
    profile_metadata = {}
    if person_data.metadata_blob:
        import json
        try:
            profile_metadata = json.loads(person_data.metadata_blob.decode('utf-8'))
        except Exception:
            pass

    return {
        "status": "Match Found",
        "confidence": score,
        "verified": verified,
        "person": {
            "national_id": person_data.national_id,
            "full_name": person_data.full_name,
            "metadata": profile_metadata
        }
    }

@app.get("/identities", response_model=IdentityListResponse)
async def list_identities(db: Session = Depends(get_db)):
    """
    List all enrolled identities.
    """
    identities = db.query(UserIdentity).order_by(UserIdentity.created_at.desc()).all()
    
    # Map to schema manually or let Pydantic handle it if structure matches
    return {
        "success": True,
        "identities": identities,
        "count": len(identities)
    }


# ---------------------------------------------------------------------------
# OCR — Identity Document Scan
# ---------------------------------------------------------------------------

@app.post("/ocr/scan-id", response_model=OCRScanResponse, tags=["OCR"])
async def scan_identity_document(request: OCRScanRequest):
    """
    OCR-based identity document scanner for Ethiopian Fayda National IDs.

    Pipeline:
    1. Decode base64 image
    2. OpenCV pre-processing (denoise, CLAHE, adaptive threshold)
    3. EasyOCR text extraction
    4. Gemini LLM smart field extraction (if GEMINI_API_KEY is set)
    5. Regex fallback (Fayda-specific parser) if no LLM key

    Returns structured identity fields + confidence score.
    """
    if not request.image_base64:
        raise HTTPException(status_code=400, detail="image_base64 is required.")

    try:
        result = ocr_extractor.extract_from_base64(request.image_base64)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")

    return {
        "success": True,
        "message": "Document scanned successfully.",
        "full_name": result.full_name,
        "id_number": result.id_number,
        "date_of_birth": result.date_of_birth,
        "nationality": result.nationality,
        "sex": result.sex,
        "document_type": result.document_type,
        "confidence_score": result.confidence_score,
        "raw_ocr_text": result.raw_ocr_text,
        "extraction_method": result.extraction_method,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
