from typing import Union
import numpy as np
from river.base import DriftDetector
import random
class ZScoreAnalysis(DriftDetector):
    
    def __init__(self,window_size: int, threshold: float =3.0):
        super().__init__()
        self.window_size = window_size
        self.threshold = threshold
        self._reset()
        
    def get_outliers(self):
        outliers = np.where(self.z_scores > self.threshold)[0]
        return outliers
    

    def _reset(self):
            self.reference_window = np.zeros(self.window_size, dtype=np.float32)
            self.mean = 0.0
            self.variance = 0.0
            self.n = 0
            self.drift_detected = False

    def update(self, x: Union[int, float]):
        # Update reference window
        if self.n < self.window_size:
            self.reference_window[self.n] = x
        else:
            self.reference_window[:-1] = self.reference_window[1:]
            self.reference_window[-1] = x

        # Update statistics
        self.n += 1
        if self.n == self.window_size:
            self.mean = np.mean(self.reference_window)
            self.variance = np.var(self.reference_window)

        # Compute z-score
        if self.n > self.window_size:
            z_score = abs((x - self.mean) / np.sqrt(self.variance))
            if z_score > self.threshold:
                self.drift_detected = True
                self._reset()

        return self
    
rng = random.Random(42)
detector =  ZScoreAnalysis(window_size=100, threshold=3)
