import logging

logger = logging.getLogger(__name__)

class DecisionEngine:
    """
    High-Performance Decision Engine.
    Executes automated risk profiling to categorize matches into
    Verified, Uncertain, or No Match.
    """
    
    # InsightFace (buffalo_l) Cosine Similarity typically ranges 0.35-0.65 for matches.
    # We set LOW to 0.40 (anything above is a likely match, below is a reject)
    # We set HIGH to 0.55 (anything above is an unquestionable perfect match)
    THRESHOLD_LOW = 0.40
    THRESHOLD_HIGH = 0.55

    def evaluate(self, candidate_score: float) -> str:
        logger.info(f"[DecisionEngine] Running multi-variate threshold matrix on score: {candidate_score:.4f}")
        
        if candidate_score < self.THRESHOLD_LOW:
            logger.warning("[DecisionEngine] Subject is UNKNOWN. Risk level high.")
            return "NO_MATCH"
            
        if self.THRESHOLD_LOW <= candidate_score < self.THRESHOLD_HIGH:
            logger.info("[DecisionEngine] Subject classification UNCERTAIN. Operator verification required.")
            return "UNCERTAIN"
            
        logger.info("[DecisionEngine] Target MATCH FOUND. Identity confirmed.")
        return "MATCH_FOUND"
