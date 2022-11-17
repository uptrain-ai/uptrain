import numpy as np
from oodles.core.classes.anomalies.abstract_anomaly import AbstractAnomaly


class DataDriftDDM(AbstractAnomaly):
    """
    Using the DDM data drift detection method
    to detect drift on dataset coming from a
    Binomial distribution.
    Args:
    warn_thres: Threshold for drift warning
    alarm_thres: Threshold for drift detection alarm
    """

    def __init__(self, warn_thres, alarm_thres):
        super().__init__()
        self.warn_thres = warn_thres
        self.alarm_thres = alarm_thres

        # Total number of predictions by the distribution
        self.total_count = 1
        # If drift is detected
        self.drift_detected = False

        self._reset()

    def _reset(self):
        """Reset the statistics."""
        # Number of predictions before the next drift
        self.current_count = 1
        # Estimated mean of the Binomial distribution
        self.mean = 1
        # Estimated standard deviation of the Binomial distribution
        self.std = 0
        # If drift is in warning zone
        self.is_warning_zone = False
        self.ms_min = np.Inf
        self.mean_min = np.Inf
        self.std_min = np.Inf

    def add_prediction(self, prediction):
        """
        Checks for data drift in the binomial distribution
        Parameters
        ----------
        prediction : Current prediction by the Binomial distribution

        Returns
        -------
        drift_detected : boolean
        """
        if self.drift_detected is True:
            self._reset()

        self.mean += (prediction - self.mean) / self.current_count
        self.std = np.sqrt(self.mean * (1 - self.mean) / self.current_count)

        self.current_count += 1
        self.total_count += 1
        self.drift_detected = False

        if self.current_count < 500:
            return False

        if self.mean + self.std <= self.ms_min:
            self.mean_min = self.mean
            self.std_min = self.std
            self.ms_min = self.mean + self.std

        if self.mean + self.std > self.mean_min + self.alarm_thres * self.std_min:
            self.drift_detected = True
            print("Data drift detected with DDM at time: ", self.current_count)
        elif self.mean + self.std > self.mean_min + self.warn_thres * self.std_min:
            self.is_warning_zone = True
        else:
            self.is_warning_zone = False

        return self.drift_detected

    def check(self, inputs, outputs, extra_args={}):
        if "y_test" in inputs.keys():
            y_gt = inputs["y_test"]
            y_pred = outputs

            for i, _ in enumerate(y_pred):
                if y_pred[i] == y_gt[i]:
                    out = self.add_prediction(0)
                else:
                    out = self.add_prediction(1)
                if out:
                    break

    def is_data_interesting(self, inputs, outputs, extra_args={}):
        return False
