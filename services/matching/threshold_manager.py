from configs.settings import get_settings

_settings = get_settings()


class ThresholdManager:
    """
    Dynamic threshold management based on security level.

    Thresholds are cosine-similarity scores in [0, 1].
    Higher threshold = stricter match (lower False Accept Rate).

    These are calibrated for ArcFace 512-dim embeddings.  The MATCH_THRESHOLD
    setting from configs/settings.py is used as the floor so that the resolver
    always has a sensible fallback.
    """

    # Tiered thresholds — tuned for real-world ArcFace distributions
    _THRESHOLDS = {
        "CRITICAL": 0.68,   # Very strict — government/border use
        "HIGH":     0.55,   # Strict but practical
        "STANDARD": 0.42,   # Standard verification
        "LOW":      0.35,   # Permissive — soft matching / candidate shortlist
    }

    # Confidence-level labels returned to callers
    _CONFIDENCE_LABELS = {
        "CRITICAL": [(0.85, "VERY_HIGH"), (0.75, "HIGH"), (0.68, "MEDIUM")],
        "HIGH":     [(0.80, "VERY_HIGH"), (0.65, "HIGH"), (0.55, "MEDIUM")],
        "STANDARD": [(0.75, "VERY_HIGH"), (0.55, "HIGH"), (0.42, "MEDIUM")],
        "LOW":      [(0.65, "VERY_HIGH"), (0.50, "HIGH"), (0.35, "MEDIUM")],
    }

    def get_threshold(self, security_level: str = "HIGH") -> float:
        level = security_level.upper()
        base = self._THRESHOLDS.get(level, self._THRESHOLDS["HIGH"])
        # Never go below the system-wide configured minimum
        return max(base, _settings.MATCH_THRESHOLD)

    def get_confidence_label(self, score: float, security_level: str = "HIGH") -> str:
        level = security_level.upper()
        tiers = self._CONFIDENCE_LABELS.get(level, self._CONFIDENCE_LABELS["HIGH"])
        for min_score, label in tiers:
            if score >= min_score:
                return label
        return "LOW"
