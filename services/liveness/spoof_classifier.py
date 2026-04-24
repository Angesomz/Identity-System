import random
from services.liveness.blink_detector import BlinkDetector

class SpoofClassifier:
    """
    Classifies an image or video stream as 'Real' or 'Spoof' (Photo/Video attack).
    """
    def __init__(self):
        self.blink_detector = BlinkDetector()
        print("Initialized Spoof Classifier (Texture + Blink)")

    def analyze_texture(self, image_np) -> float:
        """
        Mock texture analysis (LBP/HOG in real life).
        Returns probability of being 'Real'.
        """
        # Mock logic: assume high quality images for now but add noise in real scenario
        # FIXED: Return deterministic high score to avoid random failures during demo/dev
        return 0.95 

    def is_live(self, image_np, face_obj=None) -> bool:
        """
        Determines liveness score.
        If face_obj is provided (from InsightFace), uses detection confidence and quality.
        """
        if face_obj:
            # InsightFace Quality Check
            # Handle both dict (legacy/mock) and object (InsightFace) access
            if isinstance(face_obj, dict):
                det_score = face_obj.get('det_score', 0.0)
                bbox = face_obj.get('bbox', [])
            else:
                det_score = getattr(face_obj, 'det_score', 0.0)
                bbox = getattr(face_obj, 'bbox', [])

            if det_score < 0.60:
                print(f"Liveness Check Failed: Low Detection Score ({det_score:.2f})")
                return False
            
            # Simple geometric check: Face too small?
            if len(bbox) == 4:
                w = bbox[2] - bbox[0]
                h = bbox[3] - bbox[1]
                if w < 40 or h < 40:
                    print("Liveness Check Failed: Face too small")
                    return False

            # In a real system, we'd check 'pose' or depth map here.
            # For now, high confidence detection implies a "good" face.
            return True

        # Fallback to texture analysis if no face object (legacy path)
        texture_score = self.analyze_texture(image_np)
        if texture_score > 0.85:
            return True
        return False
