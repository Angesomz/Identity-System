import cv2
import numpy as np

class Preprocessor:
    """
    Standardizes input images before detection.
    """
    def normalize_illumination(self, image: np.ndarray) -> np.ndarray:
        """Applies CLAHE (Contrast Limited Adaptive Histogram Equalization)."""
        if len(image.shape) == 3:
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
            cl = clahe.apply(l)
            limg = cv2.merge((cl,a,b))
            return cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
        return image

    def resize_maintain_aspect(self, image, width=640):
        (h, w) = image.shape[:2]
        r = width / float(w)
        dim = (width, int(h * r))
        return cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
