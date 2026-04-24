
import numpy as np
import cv2
from insightface.app import FaceAnalysis

class BiometricEngine:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BiometricEngine, cls).__new__(cls)
            # Use 'buffalo_l' (large model) for better accuracy
            cls._instance.app = FaceAnalysis(name='buffalo_l')
            cls._instance.app.prepare(ctx_id=0, det_size=(640, 640))
            print("Initialized InsightFace Engine (Buffalo_L)")
        return cls._instance

    def analyze_face(self, image_np: np.ndarray):
        """
        Detects, aligns, and embeds faces in one pass.
        Returns a list of face objects (bbox, kps, embedding).
        """
        faces = self.app.get(image_np)
        return faces
