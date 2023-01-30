import numpy as np

class L2Distance():

    def compute_distance(self, base, ref) -> float:
        base = np.array(base)
        ref = np.array(ref)
        base_shape = list(base.shape)
        return np.sum((base - ref) * (base - ref), axis=tuple(range(1,len(base_shape))))