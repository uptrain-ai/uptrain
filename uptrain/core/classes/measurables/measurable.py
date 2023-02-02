import numpy as np

from uptrain.core.lib.helper_funcs import extract_data_points_from_batch, combine_data_points_for_batch
from uptrain.core.classes.anomalies.measurables import AbstractMeasurable


class Measurable(AbstractMeasurable):
    def __init__(self, framework) -> None:
        super().__init__()
        self.framework = framework
        self.cache_present_or_not = None

    def compute_and_log(self, inputs=None, outputs=None, gts=None, extra=None) -> None:
        if self.framework.use_cache:
            if self.cache_present_or_not is None:
                self.cache_present_or_not = 1
                self.framework.cache.update({self.col_name(): {}})

            compute_masks = []
            compute_idxs = []
            non_compute_vals = []
            for idx in range(len(extra['id'])):
                id = extra['id'][idx]
                if id in self.framework.cache[self.col_name()]:
                    compute_masks.append(0)
                    non_compute_vals.append(self.framework.cache[self.col_name()][id])
                else:
                    compute_masks.append(1)
                    compute_idxs.append(idx)

            compute_masks = np.array(compute_masks)
            compute_idxs = np.array(compute_idxs)

            compute_vals = self._compute(
                inputs = extract_data_points_from_batch(inputs, compute_idxs),
                outputs = extract_data_points_from_batch(outputs, compute_idxs),
                gts = extract_data_points_from_batch(gts, compute_idxs),
                extra = extract_data_points_from_batch(extra, compute_idxs)
            )

            #TODO: Replace below for loop by numpy operations
            vals = []
            compute_offset = 0
            non_compute_offset = 0
            for idx in range(len(extra['id'])):
                if compute_masks[idx] == 1:
                    vals.append(extract_data_points_from_batch(compute_vals, [compute_offset]))
                    compute_offset += 1
                else:
                    vals.append(extract_data_points_from_batch(non_compute_vals, [non_compute_offset]))
                    non_compute_offset += 1
            vals = combine_data_points_for_batch(vals)
            try:
                self._log(extra["id"], vals)
            except:
                print("Error in logging")
                import pdb; pdb.set_trace()
        else:
            vals = self._compute(inputs=inputs, outputs=outputs, gts=gts, extra=extra)
        return vals

    def _log(self, ids, vals) -> None:
        self.framework.log_measurable(ids, vals, self.col_name())
