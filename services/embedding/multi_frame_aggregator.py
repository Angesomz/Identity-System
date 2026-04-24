import numpy as np
from typing import List
from configs.settings import get_settings

settings = get_settings()

class MultiFrameAggregator:
    """
    Selects the best frames from a video stream for enrollment.
    """
    def select_best_frames(self, frames_with_scores: List[tuple], count=3) -> List[np.ndarray]:
        """
        Input: List of (image, quality_score)
        Output: Top 'count' images based on quality.
        """
        # Sort by score descending
        sorted_frames = sorted(frames_with_scores, key=lambda x: x[1], reverse=True)
        return [f[0] for f in sorted_frames[:count]]
