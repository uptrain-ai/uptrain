import numpy as np
from scipy import stats

class ZScoreAnalysis:
    
    def __init__(self, signal_value):
        self.signal_value = signal_value
        self.threshold = 3.0
        self.z_scores = np.abs(stats.zscore(signal_value))
        
    def get_outliers(self):
        outliers = np.where(self.z_scores > self.threshold)[0]
        return outliers