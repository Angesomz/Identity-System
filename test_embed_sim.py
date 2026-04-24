import cv2
from services.face_processing.engine import BiometricEngine
from services.embedding.arcface_engine import ArcFaceEngine
import numpy as np

# Load engine
app = BiometricEngine()
embedder = ArcFaceEngine()

# You can capture from webcam, but here we just wait for a second to initialize
print("Model loaded.")
