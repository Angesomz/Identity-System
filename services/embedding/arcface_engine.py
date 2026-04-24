
import numpy as np
from services.face_processing.engine import BiometricEngine

class ArcFaceEngine:
    """
    Wrapper for InsightFace embedding generation.
    """
    def __init__(self):
        self.engine = BiometricEngine()
        print("Initialized ArcFace Engine (InsightFace Backend)")

    def get_embedding(self, face_image: np.ndarray, face_obj=None) -> np.ndarray:
        """
        Returns the embedding. 
        If 'face_obj' is provided (from detector), returns its pre-computed embedding.
        Otherwise, runs analysis on the crop (less efficient).
        """
        if face_obj:
            embedding = face_obj.embedding
        else:
            # Fallback: re-analyze the crop (not recommended for speed)
            faces = self.engine.analyze_face(face_image)
            if not faces:
                raise ValueError("No face found in the crop for embedding")
            embedding = faces[0].embedding

        # Normalize logic is already handled by InsightFace, but ensuring unit length is good practice
        norm = np.linalg.norm(embedding)
        return embedding / norm
