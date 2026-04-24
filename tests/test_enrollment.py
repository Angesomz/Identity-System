import requests
import base64
import json
import cv2
import numpy as np

# Configuration
BASE_URL = "http://localhost:8001"
HEADERS = {"Content-Type": "application/json"}

def create_dummy_image():
    """Creates a simple 100x100 white image with a black square in the middle."""
    # Create valid image data
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    img.fill(255) # White
    cv2.rectangle(img, (25, 25), (75, 75), (0, 0, 0), -1) # Black box
    
    # Encode to base64
    _, buffer = cv2.imencode('.jpg', img)
    img_str = base64.b64encode(buffer).decode('utf-8')
    return img_str

def main():
    print("Generating dummy data...")
    dummy_image = create_dummy_image()
    
    # 1. Health Check
    try:
        resp = requests.get(f"{BASE_URL}/health")
        print(f"\n[GET /health] Status: {resp.status_code}")
        print(resp.json())
    except Exception as e:
        print(f"Failed to connect to server: {e}")
        return

    # 2. Enroll
    print("\n[POST /enroll] Attempting enrollment...")
    enroll_payload = {
        "national_id": "TEST_001",
        "full_name": "Test User",
        "image_base64": dummy_image,
        "metadata": {"type": "dummy_test"}
    }
    
    try:
        # Note: Auth is skipped/mocked based on code review, but if it fails we might need a token
        # The main.py has `Depends(verify_token)` so we need a token?
        # Let's check if we can bypass or generate one.
        # For now, try without token.
        resp = requests.post(f"{BASE_URL}/enroll", json=enroll_payload) # Headers missing auth
        print(f"Status: {resp.status_code}")
        print(resp.text)
        
        if resp.status_code == 403 or resp.status_code == 401:
             print("Auth required. Using mock token if possible.")
             # Create simple token if we had the key, but we don't easily have it without importing.
             # Actually, main.py imports verify_token. 
             # Let's see if we can generate a valid token.
             # For this test, valid token generation is complex without the secret key.
             # However, we have access to settings.py.
             pass

    except Exception as e:
        print(f"Enrollment failed: {e}")

if __name__ == "__main__":
    main()
