import numpy as np

class NormRatio():

    def compute_distance(self, base, ref) -> float:
        base = np.array(base)
        ref = np.array(ref)
        base_norm = np.linalg.norm(base, axis=1)
        ref_norm = np.linalg.norm(ref, axis=1)
        return base_norm / np.maximum(ref_norm, 1e-6)