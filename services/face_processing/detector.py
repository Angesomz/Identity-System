
import numpy as np
from services.face_processing.engine import BiometricEngine

class FaceDetector:
    """Wrapper for InsightFace detection."""
    
    def __init__(self):
        self.engine = BiometricEngine()
        print("Initialized RetinaFace Detector (InsightFace Backend)")

    def detect(self, image_np: np.ndarray):
        """
        Delegates detection to the shared BiometricEngine.
        Returns a list of dicts compatible with the old API.
        """
        if image_np is None or image_np.size == 0:
            return []
            
        faces = self.engine.analyze_face(image_np)
        
        results = []
        for face in faces:
            results.append({
                "bbox": face.bbox.astype(int).tolist(),
                "score": float(face.det_score),
                "landmarks": face.kps.tolist(),
                # Store the full face object to reuse embedding later if needed
                "_face_obj": face 
            })
        return results
