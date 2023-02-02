from abc import ABC


class AbstractMeasurable(ABC):
    def __init__(self) -> None:
        super().__init__()

    def _compute(self, inputs=None, outputs=None, gts=None, extra=None) -> any:
        raise Exception("Should be defined for each individual class")
