
import insightface
from insightface.app import FaceAnalysis
import sys
import os

def download_model():
    print("Attempting to initialize FaceAnalysis to trigger model download...")
    try:
        # This will trigger the download of 'buffalo_s' if not present
        app = FaceAnalysis(name='buffalo_s')
        app.prepare(ctx_id=0, det_size=(640, 640))
        print("✅ Model 'buffalo_s' loaded successfully!")
    except Exception as e:
        print(f"❌ Model load/download failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    download_model()
