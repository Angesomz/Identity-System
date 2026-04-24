import numpy as np
from scipy.spatial import distance as dist

class BlinkDetector:
    """
    Detects blinks using Eye Aspect Ratio (EAR).
    """
    def __init__(self, ear_threshold=0.25, consecutive_frames=3):
        self.ear_threshold = ear_threshold
        self.consecutive_frames = consecutive_frames
        self.counter = 0

    def eye_aspect_ratio(self, eye):
        A = dist.euclidean(eye[1], eye[5])
        B = dist.euclidean(eye[2], eye[4])
        C = dist.euclidean(eye[0], eye[3])
        ear = (A + B) / (2.0 * C)
        return ear

    def detect(self, left_eye_landmarks, right_eye_landmarks) -> bool:
        # Landmarks expected to be 6 points per eye
        leftEAR = self.eye_aspect_ratio(left_eye_landmarks)
        rightEAR = self.eye_aspect_ratio(right_eye_landmarks)
        ear = (leftEAR + rightEAR) / 2.0

        if ear < self.ear_threshold:
            self.counter += 1
        else:
            if self.counter >= self.consecutive_frames:
                self.counter = 0
                return True # Blink Detected
            self.counter = 0
        return False
