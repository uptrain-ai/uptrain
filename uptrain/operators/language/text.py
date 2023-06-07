"""
Implement oeprators over text data. 
"""

from __future__ import annotations
import re
import typing as t
from urllib.parse import urlparse

from loguru import logger
from pydantic import BaseModel, Field
import polars as pl

if t.TYPE_CHECKING:
    from uptrain.framework.config import *
from uptrain.operators.base import *

__all__ = ["DocsLinkVersion", "TextLength", "TextComparison"]


class SchemaDocumentLinks(BaseModel):
    in_col_text: str
    out_col: str = get_output_col_name_at(0)


@register_op
class DocsLinkVersion(BaseModel):
    domain_name: t.Optional[str] = None  # filter down to links from this domain
    dataschema: SchemaDocumentLinks

    def make_executor(self, settings: t.Optional[Settings] = None):
        return DocsVersionExecutor(self)


class DocsVersionExecutor(OperatorExecutor):
    op: DocsLinkVersion

    def __init__(self, op: DocsLinkVersion):
        self.op = op

    def run(self, data: pl.DataFrame) -> TYPE_OP_OUTPUT:
        def fetch_version(text):
            for link in extract_links(text, self.op.domain_name):
                v = extract_version(link)
                if v is not None:
                    return v
            return None

        df = data.with_columns(
            [
                pl.col(self.op.dataschema.in_col_text)
                .apply(fetch_version)
                .alias(self.op.dataschema.out_col)
            ]
        )
        return {"output": df}


# Text Length
class SchemaTextLength(BaseModel):
    in_col_text: str
    out_col: str = get_output_col_name_at(0)


@register_op
class TextLength(BaseModel):
    dataschema: SchemaTextLength = Field(default_factory=SchemaTextLength)

    def make_executor(self, settings: t.Optional[Settings] = None):
        return TextLengthExecutor(self)


class TextLengthExecutor(OperatorExecutor):
    op: TextLength

    def __init__(self, op: TextLength):
        self.op = op

    def run(self, data: pl.DataFrame) -> TYPE_OP_OUTPUT:
        text = data.get_column(self.op.dataschema.in_col_text)
        results = [len(i) for i in text]
        return {
            "output": data.with_columns(
                [pl.Series(self.op.dataschema.out_col, results)]
            )
        }


# Text Comparison
class SchemaTextComparison(BaseModel):
    in_col_text: str
    out_col: str = get_output_col_name_at(0)


@register_op
class TextComparison(BaseModel):
    dataschema: SchemaTextComparison = Field(default_factory=SchemaTextComparison)
    reference_text: str

    def make_executor(self, settings: t.Optional[Settings] = None):
        return TextComparisonExecutor(self)


class TextComparisonExecutor(OperatorExecutor):
    op: TextComparison

    def __init__(self, op: TextComparison):
        self.op = op

    def run(self, data: pl.DataFrame) -> TYPE_OP_OUTPUT:
        text = data.get_column(self.op.dataschema.in_col_text)
        results = [int(x == self.op.reference_text) for x in text]
        return {
            "output": data.with_columns(
                [pl.Series(self.op.dataschema.out_col, results)]
            )
        }


# -----------------------------------------------------------
# Utility routines
# -----------------------------------------------------------


def extract_links(text, base_domain=None):
    pattern = r"\bhttps?://\S+\b"
    matches = re.findall(pattern, text)
    if base_domain is not None:
        return [m for m in matches if base_domain in m]
    else:
        return matches


def extract_version(url):
    patterns = [
        r"v\d+\.\d+\.\d+",
        r"v\d+",
        r"\d+\.\d+\.\d+",
        r"\d+\.\d+",
        r"\d+",
    ]
    pattern = r"|".join([r"^" + s + r"$" for s in patterns])

    path_strings = urlparse(url).path.split("/")
    for s in path_strings:
        match = re.search(pattern, s)
        if match:
            return match.group()
    return None
