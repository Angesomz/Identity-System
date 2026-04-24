import cv2
import numpy as np
from typing import List

class FaceAligner:
    """Standard 5-point face alignment for consistent embedding generation."""
    
    def __init__(self, output_size=(112, 112)):
        self.output_size = output_size
        self.reference_pts = np.array([
            [30.2946, 51.6963],  # left eye
            [65.5318, 51.5014],  # right eye
            [48.0252, 71.7366],  # nose tip
            [33.5493, 92.3655],  # left mouth corner
            [62.7299, 92.2041]   # right mouth corner
        ], dtype=np.float32)
        if output_size[0] == 112:
             self.reference_pts[:,0] += 8.0

    def align(self, image: np.ndarray, landmarks: List[List[float]]) -> np.ndarray:
        """
        Aligns the face based on detected landmarks using similarity transform.
        """
        src_pts = np.array(landmarks, dtype=np.float32)
        ref_pts = self.reference_pts

        tfm = cv2.estimateAffinePartial2D(src_pts, ref_pts)[0]
        aligned_face = cv2.warpAffine(image, tfm, (self.output_size[0], self.output_size[1]))
        
        return aligned_face
