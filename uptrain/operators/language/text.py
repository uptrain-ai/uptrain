"""
Implement oeprators over text data. 
"""

from __future__ import annotations
import re
import typing as t
from urllib.parse import urlparse

from loguru import logger
import polars as pl
from uptrain.framework import Settings

if t.TYPE_CHECKING:
    from uptrain.framework import Settings
from uptrain.operators.base import *


@register_op
class DocsLinkVersion(ColumnOp):
    domain_name: t.Optional[str] = None  # filter down to links from this domain
    col_in_text: str

    def setup(self, settings: Settings | None = None):
        return self

    def run(self, data: pl.DataFrame) -> TYPE_COLUMN_OUTPUT:
        def fetch_version(text):
            for link in extract_links(text, self.domain_name):
                v = extract_version(link)
                if v is not None:
                    return v
            return None

        return {
            "output": data.get_column(self.col_in_text)
            .apply(fetch_version)
            .alias(get_output_col_name_at(0))
        }


@register_op
class TextLength(ColumnOp):
    col_in_text: str

    def setup(self, settings: Settings | None = None):
        return self

    def run(self, data: pl.DataFrame) -> TYPE_COLUMN_OUTPUT:
        return {
            "output": data.get_column(self.col_in_text)
            .apply(len)
            .alias(get_output_col_name_at(0))
        }


# Text Comparison
@register_op
class TextComparison(ColumnOp):
    reference_text: str
    col_in_text: str

    def setup(self, settings: Settings | None = None):
        return self

    def run(self, data: pl.DataFrame) -> TYPE_COLUMN_OUTPUT:
        return {
            "output": data.get_column(self.col_in_text)
            .apply(lambda x: int(x == self.reference_text))
            .alias(get_output_col_name_at(0))
        }


# Check if a Keyword exists in input text
@register_op
class KeywordDetector(ColumnOp):
    col_in_text: str
    keyword: str

    def setup(self, _: t.Optional[Settings] = None):
        return self

    def run(self, data: pl.DataFrame) -> TYPE_COLUMN_OUTPUT:
        return {
            "output": data.get_column(self.col_in_text)
            .apply(lambda sql: self.keyword in sql)
            .alias(get_output_col_name_at(0))
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
