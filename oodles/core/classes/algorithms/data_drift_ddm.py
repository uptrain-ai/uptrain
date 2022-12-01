import numpy as np


class DataDriftDDM:
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
            # self._reset()
            return

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
            print("Drift detected with DDM at time: ", self.total_count)
        elif self.mean + self.std > self.mean_min + self.warn_thres * self.std_min:
            self.is_warning_zone = True
        else:
            self.is_warning_zone = False
