import numpy as np
from vector_cluster.shard_router import get_shard_router


class VectorIndex:
    """
    Thin wrapper for vector add / search operations.

    Previously this created a standalone FAISSManager at the default
    ``vector_cluster/index.faiss`` path — completely disconnected from the
    ShardRouter used during enrollment.  It now delegates to the singleton
    ShardRouter so that *the same shards* are used for both writes and reads.
    """

    def __init__(self):
        # Use the process-wide singleton so we never hit a fresh, empty index
        self.router = get_shard_router()

    def search(self, vector: np.ndarray, top_k: int = 5):
        """Fan-out search across all shards, returns [(user_id, score), ...]."""
        return self.router.distribute_search(vector, k=top_k)

    def add(self, vector: np.ndarray, identity_id: int):
        """Route add to the correct shard."""
        self.router.route_add(vector, identity_id)
