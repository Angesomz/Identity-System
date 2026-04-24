import numpy as np
import faiss
import os
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Base directory is always the project root (two levels up from this file)
_BASE_DIR = Path(__file__).resolve().parent.parent


class FAISSManager:
    """
    Manages a FAISS vector index with ID support.
    Uses IndexIDMap(IndexFlatIP) for exact cosine similarity search.

    Persistence:
    - The index is saved to disk after every write (add_vectors).
    - An ID-map metadata file (.json) is maintained alongside the index so
      the set of enrolled IDs survives restarts.
    - If the .faiss file is corrupted or missing, the manager creates a fresh
      index automatically. The .json metadata is kept in sync.
    """

    def __init__(self, dimension: int = 512, index_path: str = "vector_cluster/index.faiss"):
        self.dimension = dimension

        # Always resolve to an absolute path relative to the project root
        self.index_path = str(_BASE_DIR / index_path)
        self.meta_path = self.index_path.replace(".faiss", "_meta.json")

        # Ensure the directory exists
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)

        self.index: faiss.Index = None
        self._enrolled_ids: set = set()

        self._load_or_create()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_or_create(self):
        """Try to load an existing index, fall back to creating a new one."""
        if os.path.exists(self.index_path):
            try:
                self.index = faiss.read_index(self.index_path)
                logger.info(f"[FAISS] Loaded index from {self.index_path} "
                            f"(ntotal={self.index.ntotal})")
                self._load_metadata()
                return
            except Exception as exc:
                logger.warning(f"[FAISS] Failed to load index ({exc}). "
                               "Creating a fresh index...")

        self._create_new_index()

    def _create_new_index(self):
        logger.info(f"[FAISS] Creating new IndexIDMap(IndexFlatIP) at {self.index_path}")
        base_index = faiss.IndexFlatIP(self.dimension)
        self.index = faiss.IndexIDMap(base_index)
        self._enrolled_ids = set()

    def _load_metadata(self):
        """Load the set of enrolled IDs from the companion JSON file."""
        if os.path.exists(self.meta_path):
            try:
                with open(self.meta_path, "r") as f:
                    data = json.load(f)
                self._enrolled_ids = set(data.get("enrolled_ids", []))
                logger.info(f"[FAISS] Meta loaded: {len(self._enrolled_ids)} enrolled IDs")
            except Exception as exc:
                logger.warning(f"[FAISS] Could not read metadata ({exc}).")
                self._enrolled_ids = set()
        else:
            self._enrolled_ids = set()

    def _save_metadata(self):
        """Persist the enrolled ID set alongside the index file."""
        try:
            with open(self.meta_path, "w") as f:
                json.dump({"enrolled_ids": list(self._enrolled_ids)}, f)
        except Exception as exc:
            logger.error(f"[FAISS] Failed to save metadata: {exc}")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add_vectors(self, vectors: np.ndarray, ids: np.ndarray):
        """
        Add L2-normalised vectors with custom int64 IDs.

        vectors : np.ndarray  shape (N, dim)  float32
        ids     : np.ndarray  shape (N,)       int64
        """
        vectors = np.atleast_2d(vectors).astype("float32")
        ids = np.atleast_1d(ids).astype("int64")

        # Skip duplicates — re-adding the same ID would corrupt the index
        new_mask = np.array([i not in self._enrolled_ids for i in ids])
        if not new_mask.any():
            logger.info("[FAISS] All IDs already enrolled; skipping add.")
            return

        vectors = vectors[new_mask]
        ids = ids[new_mask]

        # Normalise for cosine similarity (inner product of unit vectors == cosine)
        faiss.normalize_L2(vectors)

        self.index.add_with_ids(vectors, ids)

        for i in ids:
            self._enrolled_ids.add(int(i))

        self.save()
        logger.info(f"[FAISS] Added {len(ids)} vector(s). ntotal={self.index.ntotal}")

    def search(self, query_vector: np.ndarray, k: int = 5):
        """
        Return (distances, labels) for top-k nearest neighbours.
        Returns cosine-similarity scores in [−1, 1] (higher = better match).
        """
        query = np.atleast_2d(query_vector).astype("float32")
        faiss.normalize_L2(query)

        # FAISS raises if k > ntotal
        effective_k = min(k, max(self.index.ntotal, 1))
        distances, labels = self.index.search(query, effective_k)

        return distances, labels

    def save(self):
        """Atomically persist the index and its metadata to disk."""
        tmp_path = self.index_path + ".tmp"
        try:
            faiss.write_index(self.index, tmp_path)
            os.replace(tmp_path, self.index_path)   # atomic on most OSes
            self._save_metadata()
            logger.info(f"[FAISS] Index saved → {self.index_path} (ntotal={self.index.ntotal})")
        except Exception as exc:
            logger.error(f"[FAISS] Save failed: {exc}")
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    @property
    def ntotal(self) -> int:
        return self.index.ntotal if self.index else 0

    @property
    def enrolled_ids(self) -> set:
        return set(self._enrolled_ids)
