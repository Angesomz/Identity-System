import random
from typing import List

class ChallengeEngine:
    """
    Generates active liveness challenges (e.g., 'Turn Left', 'Blink').
    """
    def __init__(self):
        self.challenges = ["BLINK", "SMILE", "TURN_LEFT", "TURN_RIGHT"]

    def generate_challenge(self) -> str:
        return random.choice(self.challenges)

    def verify_response(self, challenge: str, action_detected: str) -> bool:
        return challenge == action_detected
