
from services.liveness.spoof_classifier import SpoofClassifier
import numpy as np
import sys

# Mocking cv2 if not present/working in headless env (though user has it)
# but for safety let's just use the classifier directly.

try:
    classifier = SpoofClassifier()
    fake_img = np.zeros((100, 100, 3), dtype=np.uint8)

    print("Testing liveness check 20 times:")
    failures = 0
    for i in range(20):
        result = classifier.is_live(fake_img)
        print(f"Run {i+1}: {result}")
        if not result:
            failures += 1
            
    print(f"\nTotal failures: {failures}/20")
    if failures > 0:
        print("CONFIRMED: Random failures detected.")
    else:
        print("No failures detected (might be lucky or logic is different).")
        
except Exception as e:
    print(f"Error running reproduction: {e}")
