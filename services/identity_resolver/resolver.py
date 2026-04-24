import logging
from sqlalchemy.orm import Session
from typing import List, Optional
from database.models import UserIdentity, AuditLog
from vector_cluster.shard_router import get_shard_router
from services.matching.threshold_manager import ThresholdManager
from configs.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()
_threshold_manager = ThresholdManager()


class IdentityResolver:
    """
    Core business logic for resolving an identity from vector search results.
    Combines vector similarity scores with risk rules and database metadata.

    Match strategy
    --------------
    1. Fan-out distributed vector search across all FAISSManager shards.
    2. Filter candidates by a tiered similarity threshold.
       If the strict tier yields no match, we fall back to a softer tier
       and still return a result (marked MEDIUM/LOW confidence) so the
       caller can decide what to do — preventing the "match not found" for
       borderline faces.
    3. Retrieve final metadata from the SQL database.
    4. Async-safe audit log.
    """

    def __init__(self, db: Session, shard_router=None):
        self.db = db
        # Accept an injected router but default to the process singleton so
        # callers that don't pass one still hit the correct shards.
        self.router = shard_router if shard_router is not None else get_shard_router()
        self.threshold_manager = _threshold_manager

    def search_similar_faces(self, query_vector, top_k: int = 5) -> List[dict]:
        """
        Retrieval System: Distributes search to Vector Indexes (FAISS).
        Returns raw candidates without running business logic thresholds.
        """
        raw_matches = self.router.distribute_search(query_vector, k=top_k)
        candidates = []
        for identity_id, score in raw_matches:
            candidates.append({"id": int(identity_id), "score": float(score)})
        return candidates

    def get_person_record(self, identity_id: int) -> Optional[UserIdentity]:
        """
        Identity Database: Retrieves the exact individual from the Intelligence SQL Database.
        """
        identity = self.db.query(UserIdentity).filter(UserIdentity.id == identity_id).first()
        return identity

    def resolve_identity(
        self,
        query_vector,
        top_k: int = 5,
        security_level: str = "HIGH",
    ) -> List[dict]:
        """
        1. Vector search across shards.
        2. Threshold filtering with soft-fallback.
        3. DB metadata lookup.
        4. Audit logging.
        """
        # 1. Distributed vector search
        raw_matches = self.router.distribute_search(query_vector, k=top_k)
        logger.info(f"[Resolver] distribute_search returned {len(raw_matches)} candidate(s)")

        if not raw_matches:
            self._log_search(query_vector, [])
            return []

        results = self._filter_and_enrich(raw_matches, security_level)

        # Soft fallback: if strict threshold killed all results, retry at LOW
        if not results and security_level != "LOW":
            logger.info("[Resolver] Strict threshold eliminated all candidates; "
                        "retrying with LOW security threshold for soft match.")
            results = self._filter_and_enrich(raw_matches, "LOW")

        self._log_search(query_vector, results)
        return results

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _filter_and_enrich(
        self, raw_matches: list, security_level: str
    ) -> List[dict]:
        threshold = self.threshold_manager.get_threshold(security_level)
        logger.info(f"[Resolver] Using threshold={threshold:.4f} "
                    f"(security_level={security_level})")

        results = []
        for identity_id, score in raw_matches:
            if score < threshold:
                logger.debug(
                    f"[Resolver] Skipping id={identity_id} score={score:.4f} "
                    f"< threshold={threshold:.4f}"
                )
                continue

            # Cast numpy types for SQLAlchemy / psycopg2 compatibility
            identity_id_native = int(identity_id)
            identity: Optional[UserIdentity] = (
                self.db.query(UserIdentity)
                .filter(UserIdentity.id == identity_id_native)
                .first()
            )

            if identity is None:
                logger.warning(
                    f"[Resolver] Vector match id={identity_id_native} not found in DB — "
                    "index may be out of sync with the database."
                )
                continue

            confidence = self.threshold_manager.get_confidence_label(score, security_level)
            results.append(
                {
                    "national_id": identity.national_id,
                    "full_name": identity.full_name,
                    "score": round(score, 6),
                    "confidence": confidence,
                    "metadata": {
                        "full_name": identity.full_name,
                        "national_id": identity.national_id,
                        "security_level": security_level,
                    },
                }
            )

        return results

    def _log_search(self, vector, results: List[dict]):
        try:
            status = "MATCH_FOUND" if results else "NO_MATCH"
            top_score = results[0]["score"] if results else 0.0
            audit = AuditLog(
                action="SEARCH",
                request_ip="internal",
                status=status,
                confidence_score=top_score,
            )
            self.db.add(audit)
            self.db.commit()
        except Exception as exc:
            logger.error(f"[Resolver] Audit log failed: {exc}")
