"""IO operators to read from Excel files"""

from __future__ import annotations
import typing as t

import polars as pl
import deltalake as dl

if t.TYPE_CHECKING:
    from uptrain.framework import Settings
from uptrain.operators.base import *
from uptrain.utilities import lazy_load_dep

xlsx2csv = lazy_load_dep("xlsx2csv", "xlsx2csv")


@register_op
class ExcelReader(TransformOp):
    """Reads an excel file.

    Attributes:
        fpath (str): Path to the xlsx file.
        batch_size (Optional[int]): Number of rows to read at a time. Defaults to None, which reads the entire file.

    """

    fpath: str
    batch_size: t.Optional[int] = None

    def setup(self, settings: Settings):
        return self

    def run(self) -> TYPE_TABLE_OUTPUT:
        return {"output": pl.read_excel(self.fpath)}
