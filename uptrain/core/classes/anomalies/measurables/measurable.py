from uptrain.core.classes.anomalies.measurables import AbstractMeasurable


class Measurable(AbstractMeasurable):
    def __init__(self, framework) -> None:
        super().__init__()
        self.framework = framework

    def compute_and_log(self, inputs=None, outputs=None, gts=None, extra=None) -> None:
        val = self._compute(inputs=inputs, outputs=outputs, gts=gts, extra=extra)
        self._log(extra["id"][0], val)
        return val

    def _log(self, id, val) -> None:
        self.framework.log_measurable(id, val, self.col_name())
