from abc import ABC
from typing import Any


class AbstractDistance(ABC):
    def __init__(self) -> None:
        super().__init__()
    
    def compute_distance(self, base, reference) -> Any:
        raise Exception("Distance computation should be defined for each subclass")
