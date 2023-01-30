import numpy as np

from uptrain.core.classes.anomalies import AbstractAnomaly
from uptrain.core.classes.anomalies.signals import SignalManager
from uptrain.constants import Anomaly


class EdgeCase(AbstractAnomaly):
    dashboard_name = "edge_cases"
    anomaly_type = Anomaly.EDGE_CASE

    def __init__(self, fw, signal_formulae):
        self.log_handler = fw.log_handler
        self.log_handler.add_writer(self.dashboard_name)
        self.signal_manager = SignalManager()
        self.signal_manager.add_signal_formulae(signal_formulae)
        self.num_preds = 0
        self.num_selected = 0

    def check(self, inputs, outputs, gts=None, extra_args={}):
        return

    def is_data_interesting(self, inputs, outputs, gts=None, extra_args={}):
        is_interesting = self.signal_manager.evaluate_signal(
            inputs, outputs, gts=gts, extra_args=extra_args
        )
        self.num_preds += len(is_interesting)
        self.num_selected += sum(is_interesting)
        self.log_handler.add_scalars(
            "num_edge_cases",
            {"num_edge_cases": self.num_selected},
            self.num_preds,
            self.dashboard_name,
        )
        return is_interesting

    def need_ground_truth(self):
        return False
