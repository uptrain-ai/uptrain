import numpy as np


class NormRatio:
    def compute_distance(self, base, ref) -> float:
        base = np.array(base)
        ref = np.array(ref)
        if len(base.shape) > 1:
            base_norm = np.linalg.norm(base, axis=1)
        else:
            base_norm = np.abs(base)
        if len(ref.shape) > 1:
            ref_norm = np.linalg.norm(ref, axis=1)
        else:
            ref_norm = np.abs(ref)
        return base_norm / np.maximum(ref_norm, 1e-6)
