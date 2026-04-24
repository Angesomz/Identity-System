from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Tuple

import numpy as np

from vector_cluster.faiss_manager import FAISSManager

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Singleton guard — one ShardRouter per process, so shards share the same
# FAISSManager instances and never recreate (wipe) their indices.
# ---------------------------------------------------------------------------
_instance: "ShardRouter | None" = None


def get_shard_router() -> "ShardRouter":
    """Return the process-wide singleton ShardRouter."""
    global _instance
    if _instance is None:
        _instance = ShardRouter()
    return _instance


class ShardRouter:
    """
    Routes add / search requests to the correct FAISS shard.

    Sharding strategy
    -----------------
    Vectors are assigned to shards by  ``user_id % NUM_SHARDS``.
    Every shard is backed by its own ``FAISSManager`` which persists its
    index to disk.  On startup the managers load existing indices so no
    previously enrolled face is ever lost.

    Search queries are **fan-out** across all shards in parallel using a
    thread pool, and results are merged + re-ranked by cosine similarity.
    """

    NUM_SHARDS = 3

    def __init__(self):
        self.shards: dict[str, FAISSManager] = {
            f"shard_{i}": FAISSManager(index_path=f"vector_cluster/shard_{i}.faiss")
            for i in range(self.NUM_SHARDS)
        }
        total = sum(s.ntotal for s in self.shards.values())
        logger.info(f"[ShardRouter] Initialised {self.NUM_SHARDS} shards. "
                    f"Total enrolled vectors: {total}")

    # ------------------------------------------------------------------
    # Write path
    # ------------------------------------------------------------------

    def route_add(self, vector: np.ndarray, user_id: int) -> None:
        """Add a single face vector to the appropriate shard."""
        shard_key = f"shard_{user_id % self.NUM_SHARDS}"
        logger.info(f"[ShardRouter] Enrolling user_id={user_id} → {shard_key}")
        shard = self.shards[shard_key]
        shard.add_vectors(
            np.atleast_2d(vector).astype("float32"),
            np.array([user_id], dtype="int64"),
        )

    # ------------------------------------------------------------------
    # Read path — parallel fan-out
    # ------------------------------------------------------------------

    def distribute_search(
        self, query_vector: np.ndarray, k: int = 5
    ) -> List[Tuple[int, float]]:
        """
        Query **all** shards in parallel and return the top-k global results
        sorted by descending cosine similarity score.

        Returns
        -------
        List of (user_id: int, score: float) — highest score first.
        """
        all_results: List[Tuple[int, float]] = []

        def _search_shard(name: str, shard: FAISSManager):
            if shard.ntotal == 0:
                logger.debug(f"[ShardRouter] {name} is empty — skipping.")
                return []
            distances, labels = shard.search(query_vector, k)
            results = []
            for score, label in zip(distances[0], labels[0]):
                if label != -1 and score > -1:   # -1 means no result
                    results.append((int(label), float(score)))
            return results

        # Fan-out to all shards concurrently
        with ThreadPoolExecutor(max_workers=self.NUM_SHARDS) as pool:
            futures = {
                pool.submit(_search_shard, name, shard): name
                for name, shard in self.shards.items()
            }
            for future in as_completed(futures):
                shard_name = futures[future]
                try:
                    all_results.extend(future.result())
                except Exception as exc:
                    logger.error(f"[ShardRouter] {shard_name} search error: {exc}")

        # Merge & rank — higher cosine similarity is better
        all_results.sort(key=lambda x: x[1], reverse=True)
        logger.info(
            f"[ShardRouter] Distributed search returned {len(all_results)} candidates; "
            f"top score = {all_results[0][1]:.4f}" if all_results else
            "[ShardRouter] Distributed search: no candidates found"
        )
        return all_results[:k]

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def stats(self) -> dict:
        return {
            name: {"ntotal": shard.ntotal, "enrolled_ids": list(shard.enrolled_ids)}
            for name, shard in self.shards.items()
        }
