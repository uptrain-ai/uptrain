from oodles.core.classes.anomalies.abstract_anomaly import AbstractAnomaly
from oodles.core.classes.anomalies.signal_manager import SignalManager


class EdgeCaseManager(AbstractAnomaly):
    dashboard_name = 'num_edge_cases'

    def __init__(self, signal_formulae, log_args={}):
        super().__init__(log_args=log_args)
        self.signal_manager = SignalManager()
        self.signal_manager.add_signal_formulae(signal_formulae)
        self.num_preds = 0
        self.num_selected = 0

    def check(self, inputs, outputs, gts=None, extra_args={}):
        return

    def is_data_interesting(self, inputs, outputs, gts=None, extra_args={}):
        self.num_preds += 1
        is_interesting = self.signal_manager.evaluate_signal(
            inputs, outputs, gts=gts, extra_args=extra_args
        )
        self.num_selected += int(is_interesting)
        self.plot_scalar("num_edge_cases", self.num_selected, self.num_preds)
        return is_interesting

    def need_ground_truth(self):
        return False
