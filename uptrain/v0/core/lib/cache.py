"""Utility routines to cache data when computing metrics
"""

from __future__ import annotations
from abc import abstractmethod
from typing import Any, Type, Protocol

import numpy as np


# -----------------------------------------------------------
# State cache
# -----------------------------------------------------------


class StateCache(Protocol):
    """Container to store intermediate state when computing aggregate statistics."""

    def __init__(self, fw: Any, columns: dict[str, Type]):
        pass

    @abstractmethod
    def upsert_ids_n_col_values(
        self, ids: np.ndarray, col_values: dict[str, np.ndarray]
    ):
        pass

    @abstractmethod
    def fetch_col_values_for_ids(
        self, ids: np.ndarray, col_names: list[str]
    ) -> list[dict]:
        pass


class DictStateCache:
    """A state cache that uses python dictionaries to store intermediate state."""

    def __init__(self, fw: Any, columns: dict[str, Type]) -> None:
        self.state_dicts = {col: {} for col in columns}

    def __del__(self) -> None:
        for container in self.state_dicts.values():
            container.clear()
        del self.state_dicts

    def upsert_ids_n_col_values(
        self, ids: np.ndarray, col_values: dict[str, np.ndarray]
    ) -> None:
        for col, values in col_values.items():
            assert len(ids) == len(values)
            container = self.state_dicts[col]
            container.update({id: value for id, value in zip(ids, values)})

    def fetch_col_values_for_ids(
        self, ids: np.ndarray, col_names: list[str]
    ) -> list[dict]:
        output = []
        for col in col_names:
            container = self.state_dicts[col]
            output.append({id: container[id] for id in ids if id in container})
        return output


def make_cache_container(fw: Any, columns: dict[str, Type]) -> StateCache:
    """Create a state cache container for the given columns."""
    if fw.config_obj.running_ee:
        try:
            from uptrain.v0.ee.lib.cache import DuckDBStateCache
        except ImportError as exc:
            print(
                "Error importing the uptrain-ee subpackage, Uptrain enterprise Edition not installed."
            )
            raise exc

        return DuckDBStateCache(fw, columns)
    else:
        return DictStateCache(fw, columns)
