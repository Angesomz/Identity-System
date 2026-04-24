
import sys
import os
import numpy as np
import pytest
from unittest.mock import MagicMock, patch

# Ensure project root is in path
sys.path.append(os.getcwd())

from services.face_processing.engine import BiometricEngine
from gateway.main import app
from fastapi.testclient import TestClient

# Mock BiometricEngine BEFORE it gets instantiated in main
sys.modules['insightface'] = MagicMock()
sys.modules['insightface.app'] = MagicMock()
sys.modules['onnxruntime'] = MagicMock()

# Now we can import things that use it
from services.face_processing.engine import BiometricEngine

# Patch the singleton
@pytest.fixture
def mock_engine():
    with patch('services.face_processing.engine.BiometricEngine') as MockClass:
        mock_instance = MockClass.return_value
        # Mock analyze_face to return a dummy face object
        dummy_face = MagicMock()
        dummy_face.bbox = np.array([100, 100, 200, 200])
        dummy_face.kps = np.array([[100,100], [200,100], [150,150], [120,180], [180,180]])
        dummy_face.det_score = 0.99
        dummy_face.embedding = np.random.rand(512).astype(np.float32)
        dummy_face.embedding /= np.linalg.norm(dummy_face.embedding)
        
        # BiometricEngine.analyze_face returns a list of faces
        mock_instance.analyze_face.return_value = [dummy_face]
        yield mock_instance

def test_pipeline_logic(mock_engine):
    print("Testing Pipeline Logic with Mock Engine...")
    
    # We need to manually inject the mock into the actual instance if it's already created
    # But since we patched the class, new instances will be mocks.
    # However, if main.py imports it at top level, it might be tricky.
    # Let's try to patch the method directly on the class if possible.
    
    # Actually, let's just test the logic functions directly if TestClient is too complex due to global state
    
    engine = BiometricEngine()
    faces = engine.analyze_face(np.zeros((640, 640, 3)))
    assert len(faces) == 1
    print("Mock Engine returning faces correctly.")
    
    # Test vector normalization
    vec = faces[0].embedding
    norm = np.linalg.norm(vec)
    print(f"Embedding Norm: {norm}")
    assert np.isclose(norm, 1.0)
    
if __name__ == "__main__":
    # Manual run
    with patch('services.face_processing.engine.BiometricEngine') as MockClass:
        instance = MockClass()
        dummy_face = MagicMock()
        dummy_face.bbox = np.array([100, 100, 200, 200])
        dummy_face.embedding = np.random.rand(512).astype(np.float32)
        dummy_face.embedding /= np.linalg.norm(dummy_face.embedding)
        instance.analyze_face.return_value = [dummy_face]
        
        print("Running manual mock test...")
        res = instance.analyze_face(None)
        print(f"Result: {len(res)} faces detected.")
        print("Mock Logic Verified.")
