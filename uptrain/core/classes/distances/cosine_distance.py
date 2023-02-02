import numpy as np

class CosineDistance():

    def compute_distance(self, base, ref) -> float:
        base = np.array(base)
        ref = np.array(ref)
        base_norm = np.linalg.norm(base, axis=1)
        ref_norm = np.linalg.norm(ref, axis=1)
        return np.array([np.dot(base[i], ref[i])/(base_norm[i]*ref_norm[i]) for i in range(base.shape[0])])
