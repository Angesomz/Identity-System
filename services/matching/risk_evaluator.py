class RiskEvaluator:
    """
    Evaluates risk of a match being a false positive.
    """
    def evaluate(self, score: float, threshold: float) -> str:
        margin = score - threshold
        
        if margin < 0:
            return "NO_MATCH"
        
        if margin < 0.05:
            return "HIGH_RISK_MATCH" # Borderline
        elif margin < 0.15:
            return "MEDIUM_RISK_MATCH"
        else:
            return "Verified"
