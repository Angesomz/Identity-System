
import sys
import os
import numpy as np
sys.path.append(os.getcwd())

from vector_cluster.faiss_manager import FAISSManager

def test_search_1d():
    print("Testing FAISSManager with 1D array...")
    manager = FAISSManager(index_path="test_index.faiss")
    
    # Create a 1D vector
    vec = np.random.rand(512).astype(np.float32)
    
    try:
        distances, labels = manager.search(vec, k=1)
        print("Success! Search returned:", distances.shape, labels.shape)
    except Exception as e:
        print("Failed with error:", e)
        sys.exit(1)
    finally:
        if os.path.exists("test_index.faiss"):
            os.remove("test_index.faiss")

if __name__ == "__main__":
    test_search_1d()
