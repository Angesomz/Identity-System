import pytest
import numpy as np
from fastapi.testclient import TestClient
from ..gateway.main import app
from ..services.face_processing.detector import FaceDetector
from ..services.embedding.arcface_engine import ArcFaceEngine
from ..vector_cluster.faiss_manager import FAISSManager

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_face_pipeline_mock():
    """Verifies that the mock AI pipeline components communicate correctly."""
    # 1. Detection
    detector = FaceDetector()
    fake_img = np.zeros((500, 500, 3), dtype=np.uint8)
    faces = detector.detect(fake_img)
    assert len(faces) == 1
    assert "bbox" in faces[0]

    # 2. Embedding
    embedder = ArcFaceEngine()
    vector = embedder.get_embedding(fake_img)
    assert vector.shape == (512,)
    assert np.isclose(np.linalg.norm(vector), 1.0) # Normalized

def test_vector_search():
    """Verifies FAISS index operations."""
    manager = FAISSManager(dimension=512, index_path="test_index.faiss")
    
    # Create random vectors
    vectors = np.random.rand(10, 512).astype('float32')
    ids = np.arange(10).astype('int64')
    
    manager.add_vectors(vectors, ids)
    
    # Search for the first vector itself
    query = vectors[0:1]
    distances, labels = manager.search(query, k=1)
    
    assert labels[0][0] == 0 # Should find itself
    assert distances[0][0] >= 0.99 # Cosine similarity of identical vector is 1.0 (or close due to float precision)
