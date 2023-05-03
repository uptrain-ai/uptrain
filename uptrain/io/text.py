from __future__ import annotations
from typing import Optional

import pandas as pd
from pydantic import BaseModel


class CsvReader(BaseModel):
    fpath: str
    columns: Optional[list[str]] = None
    batch_size: int = 50_000

    def setup(self):
        self._dataset = pd.read_csv(self.fpath, usecols=self.columns)
        self._rows_read = 0

    def run(self) -> Optional[pd.DataFrame]:
        if self._rows_read >= len(self._dataset):
            return None
        else:
            self._rows_read += self.batch_size
            return self._dataset.iloc[
                self._rows_read : self._rows_read + self.batch_size
            ]


class CsvWriter(BaseModel):
    fpath: str
    columns: Optional[list[str]] = None

    def setup(self):
        self._rows_written = 0

    def run(self, data: pd.DataFrame):
        if self.columns is None:
            self.columns = list(data.columns)
        assert set(self.columns) == set(data.columns)

        if self._rows_written == 0:
            data.to_csv(self.fpath, index=False, columns=self.columns)
        else:
            data.to_csv(
                self.fpath, index=False, columns=self.columns, mode="a", header=False
            )
        self._rows_written += len(data)
