from abc import ABC
from typing import Any

import numpy as np


class AbstractDistance(ABC):
    def __init__(self) -> None:
        super().__init__()

    def compute_distance(self, base, reference) -> Any:
        raise Exception("Distance computation should be defined for each subclass")

    def check_compatibility(self, base, reference) -> None:
        if base.shape != reference.shape:
            raise Exception("Incompatible shapes for base and reference")
