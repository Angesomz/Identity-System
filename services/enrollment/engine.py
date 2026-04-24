from sqlalchemy.orm import Session
import numpy as np
from fastapi import HTTPException
from database.models import UserIdentity
from services.liveness.spoof_classifier import SpoofClassifier
from services.face_processing.detector import FaceDetector
from services.embedding.arcface_engine import ArcFaceEngine
from vector_cluster.shard_router import get_shard_router

class EnrollmentEngine:
    """
    Orchestrates the enrollment process:
    Decode -> Detect -> Liveness -> Embed -> DB -> Index
    """
    def __init__(self):
        self.detector = FaceDetector()
        self.spoof_classifier = SpoofClassifier()
        self.embedder = ArcFaceEngine()
        self.shard_router = get_shard_router()  # singleton — shares shards with gateway

    def enroll(self, image: np.ndarray, national_id: str, full_name: str, db: Session, metadata: dict = None) -> UserIdentity:
        # 1. Detect Face
        faces = self.detector.detect(image)
        if not faces:
            raise HTTPException(status_code=400, detail="No face detected")
        
        # For enrollment, assume single face or verify there is only one
        # Here we take the primary (largest) face
        primary_face = faces[0]

        # 2. Liveness Check
        # Using the detected face object improves accuracy if supported by classifier
        # Otherwise passing the full image
        if not self.spoof_classifier.is_live(image, face_obj=primary_face.get("_face_obj")):
            raise HTTPException(status_code=400, detail="Liveness check failed: Possible spoof attempt")

        # 3. Generate Embedding
        # Extract embedding from the primary face
        vector = self.embedder.get_embedding(image, face_obj=primary_face.get("_face_obj"))

        import json
        metadata_encoded = None
        if metadata:
            # Save raw metadata as bytes
            metadata_encoded = json.dumps(metadata).encode('utf-8')

        # 4. Save to Database
        new_identity = UserIdentity(
            national_id=national_id,
            full_name=full_name,
            metadata_blob=metadata_encoded
        )
        db.add(new_identity)
        db.commit()
        db.refresh(new_identity)

        # 5. Save to Vector Index
        self.shard_router.route_add(vector, new_identity.id)

        return new_identity
