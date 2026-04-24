
import sys
import os
import cv2
import numpy as np

# Ensure project root is in path
sys.path.append(os.getcwd())

from services.face_processing.engine import BiometricEngine

def test_engine():
    print("Testing BiometricEngine...")
    try:
        engine = BiometricEngine()
        # Create a dummy image (black square)
        # InsightFace expects a valid image, might return empty if no face
        # Ideally we'd need a real face image, but let's just check initialization first
        img = np.zeros((640, 640, 3), dtype=np.uint8)
        
        print("Running analysis on dummy image...")
        faces = engine.analyze_face(img)
        print(f"Analysis complete. Found {len(faces)} faces (expected 0 for black image).")
        
    except Exception as e:
        print(f"Engine failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_engine()
