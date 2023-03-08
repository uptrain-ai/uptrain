import numpy as np

from river import drift


class DataDriftDDM(drift.DDM):
    def __init__(self, warm_start, warning_threshold, alarm_threshold):
        super().__init__(warm_start, warning_threshold, alarm_threshold)

        self.alert: str = None
        self.total_count: int = 0

        self._reset()

    def _reset(self):
        super()._reset()
        self.alert = None

    def add_prediction(self, prediction: int) -> str:
        self.total_count += 1
        self.update(prediction)

        if self.drift_detected:
            self.alert = f"Drift detected with DDM at time: {self.total_count}!!!"

        return self.alert
