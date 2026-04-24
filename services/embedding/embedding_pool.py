import numpy as np
from typing import List

class EmbeddingPool:
    """
    Manages a pool of embeddings for a single identity to improve precision.
    """
    def __init__(self, max_size=5):
        self.max_size = max_size

    def aggregate(self, embeddings: List[np.ndarray]) -> np.ndarray:
        """
        Averages multiple embeddings to create a robust template.
        """
        if not embeddings:
            return None
        
        # Stack and average
        stacked = np.stack(embeddings)
        mean_embedding = np.mean(stacked, axis=0)
        
        # Renormalize
        norm = np.linalg.norm(mean_embedding)
        return mean_embedding / norm
