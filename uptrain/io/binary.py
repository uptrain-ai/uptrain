from __future__ import annotations
from typing import Optional
import os

import pandas as pd
from pydantic import BaseModel

class ParquetReader(BaseModel):
    fpath: str
    columns: Optional[list[str]] = None
    batch_size: int = 50_000

    def setup(self):
        self._dataset = pd.read_parquet(self.fpath, columns=self.columns)
        self._rows_read = 0

    def run(self) -> Optional[pd.DataFrame]:
        if self._rows_read >= len(self._dataset):
            return None
        else:
            self._rows_read += self.batch_size
            return self._dataset.iloc[
                self._rows_read : self._rows_read + self.batch_size
            ]


class ParquetWriter(BaseModel):
    fpath: str  # can't append to a parquet file, so we write multiple files to the directory
    columns: Optional[list[str]] = None

    def setup(self):
        self.count = 0

    def run(self, data: pd.DataFrame):
        if self.columns is None:
            self.columns = list(data.columns)
        assert set(self.columns) == set(data.columns)

        fname = os.path.join(self.fpath, f"{self.count}.pq")
        data.to_parquet(fname, index=False)
        self.count += 1
