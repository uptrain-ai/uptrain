import numpy as np

from uptrain.v0.core.classes.monitors import AbstractMonitor
from uptrain.v0.core.classes.signals import SignalManager
from uptrain.v0.constants import Monitor


class EdgeCase(AbstractMonitor):
    dashboard_name = "edge_cases"
    monitor_type = Monitor.EDGE_CASE

    def base_init(self, fw, check):
        self.signal_manager = SignalManager()
        self.signal_manager.add_signal_formulae(check["signal_formulae"])
        self.num_preds = 0
        self.num_selected = 0

    def base_check(self, inputs, outputs, gts=None, extra_args={}):
        return

    def base_is_data_interesting(self, inputs, outputs, gts=None, extra_args={}):
        is_interesting = self.signal_manager.evaluate_signal(
            inputs, outputs, gts=gts, extra_args=extra_args
        )
        self.num_preds += len(is_interesting)
        self.num_selected += sum(is_interesting)
        self.log_handler.add_scalars(
            "num_edge_cases",
            {"y_num_edge_cases": self.num_selected},
            self.num_preds,
            self.dashboard_name,
        )
        reasons = []
        for is_in in is_interesting:
            if is_in:
                reasons.append(f"Signal-{str(self.signal_manager.formulae)}")
            else:
                reasons.append("None")
        return is_interesting, reasons

    def need_ground_truth(self):
        return False
