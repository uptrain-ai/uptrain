import numpy as np

from uptrain.v0.core.classes.monitors import AbstractCheck

class AbstractMonitor(AbstractCheck):
    monitor_type = None

    def need_ground_truth(self):
        return False

    def is_data_interesting(self, inputs, outputs, gts=None, extra_args={}):
        if len(self.children) > 0:
            is_interesting = np.array([False] * len(extra_args["id"]))
            reasons = ["None"] * len(extra_args["id"])
            is_interesting = []
            reasons = []
            for child in self.children:
                    res = child.is_data_interesting(
                            inputs, outputs, gts=gts, extra_args=extra_args
                        )
                    is_interesting.append(res[0])
                    reasons.append(res[1])
            if len(reasons):
                final_reason = ["None"] * len(reasons[0])
                for reas in reasons:
                    for jdx in range(len(reas)):
                        if not (reas[jdx] == "None"):
                            final_reason[jdx] = reas[jdx]
            else:
                final_reason = []
            return np.greater(np.sum(np.array(is_interesting), axis=0), 0), np.array(final_reason)
        else:
            return self.base_is_data_interesting(inputs, outputs, gts=gts, extra_args=extra_args)

    def base_is_data_interesting(self, inputs, outputs, gts=None, extra_args={}):
        return np.array([False] * len(extra_args["id"])), np.array(['None'] * len(extra_args["id"]))
