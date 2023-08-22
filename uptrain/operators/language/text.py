"""
Implement operators over text data.

This module provides several operators for processing and analyzing text data, including:
- `DocsLinkVersion`: Extracts version numbers from URLs in text data, optionally filtered by domain name.
- `TextLength`: Calculates the length of each text entry in a column.
- `TextComparison`: Compares each text entry in a column with a reference text.

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


# TODO: Add support for versions without a minor version number (e.g., "v1") or without a patch version number (e.g., "v1.2")
@register_op
class DocsLinkVersion(ColumnOp):
    """
    Operator to extract version numbers from URLs in text data.

    Attributes:
        domain_name (str, optional): Filter down to links from this domain. Defaults to None.
        col_in_text (str): The name of the input column containing the text data.

    Returns:
        dict: A dictionary containing the extracted version numbers.

    Example:
        ```
        import polars as pl
        from uptrain.operators import DocsLinkVersion

        # Create a DataFrame
        df = pl.DataFrame({
            "text": ["https://docs.streamlit.io/1.9.0/library/api-reference/charts/st.plotly_chart#stplotly_chart", "No version here"]
        })

        # Create an instance of the DocsLinkVersion class
        link_op = DocsLinkVersion(col_in_text="text")

        # Extract the version numbers
        versions = link_op.run(df)["output"]

        # Print the extracted version numbers
        print(versions)
        ```

    Output:
        ```
        shape: (2,)
        Series: '_col_0' [str]
        [
                "1.9.0"
                null
        ]
        ```

    """

    domain_name: t.Optional[str] = None  # filter down to links from this domain
    col_in_text: str
    col_out: str = "docs_link_version"

    def setup(self, settings: Settings):
        return self

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        def fetch_version(text):
            for link in extract_links(text, self.domain_name):
                v = extract_version(link)
                if v is not None:
                    return v
            return None

        results = data.get_column(self.col_in_text).apply(fetch_version)
        return {"output": data.with_columns([results.alias(self.col_out)])}


@register_op
class WordCount(ColumnOp):
    """
    Operator to calculate the number of words in each text entry in a column.

    Attributes:
        col_in_text (str): The name of the input column containing the text data.
        col_out (str): The name of the output column containing the number of words.

    Returns:
        dict: A dictionary containing the calculated number of words.

    Example:
        ```
        import polars as pl
        from uptrain.operators import WordCount

        # Create a DataFrame
        df = pl.DataFrame({
            "text": ["This is a sample text.", "Another example sentence.", "Yet another sentence."]
        })

        # Create an instance of the WordCount class
        word_count_op = WordCount(col_in_text="text")

        # Calculate the number of words in each text entry
        word_counts = word_count_op.run(df)["output"]

        # Print the word counts
        print(word_counts)
        ```

    Output:
        ```
        shape: (3,)
        Series: '_col_0' [i64]
        [
                5
                3
                3
        ]
        ```

    """

    col_in_text: str
    col_out: str = "word_count"

    def setup(self, settings: Settings):
        return self

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        results = data.get_column(self.col_in_text).apply(lambda x: len(x.split(" ")))
        return {"output": data.with_columns([results.alias(self.col_out)])}


@register_op
class TextLength(ColumnOp):
    """
    Operator to calculate the length of each text entry in a column.

    Attributes:
        col_in_text (str): The name of the input column containing the text data.
        col_out (str): The name of the output column containing the text lengths.

    Returns:
        dict: A dictionary containing the calculated text lengths.

    Example:
        ```
        import polars as pl
        from uptrain.operators import TextLength

        # Create a DataFrame
        df = pl.DataFrame({
            "text": ["This is a sample text.", "Another example sentence.", "Yet another sentence."]
        })

        # Create an instance of the TextLength class
        length_op = TextLength(col_in_text="text")

        # Calculate the length of each text entry
        lengths = length_op.run(df)["output"]

        # Print the text lengths
        print(lengths)
        ```

    Output:
        ```
        shape: (3,)
        Series: '_col_0' [i64]
        [
                22
                25
                21
        ]
        ```

    """

    col_in_text: str
    col_out: str = "text_length"

    def setup(self, settings: Settings):
        return self

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        results = data.get_column(self.col_in_text).apply(len)
        return {"output": data.with_columns([results.alias(self.col_out)])}


@register_op
class TextComparison(ColumnOp):
    """
    Operator to compare each text entry in a column with a list of reference texts.

    Attributes:
        reference_texts (Union[list[str], str]): List of reference text for comparison.
        col_in_text (str): The name of the input column containing the text data.
        col_out (str): The name of the output column containing the comparison results.

    Returns:
        dict: A dictionary containing the comparison results (1 if equal, 0 otherwise).

    Example:
        ```
        import polars as pl
        from uptrain.operators import TextComparison

        # Create a DataFrame
        df = pl.DataFrame({
            "text": ["This is a sample text.", "Another example sentence.", "Yet another sentence."]
        })

        # Set the reference text for comparison
        ref_text = ["This is a sample text.", "Yet another sentence."]

        # Create an instance of the TextComparison class
        comp_op = TextComparison(reference_texts=ref_text, col_in_text="text")

        # Compare each text entry with the reference text
        comparison = comp_op.run(df)["output"]

        # Print the comparison results
        print(comparison)
        ```

    Output:
        ```
        shape: (3,)
        Series: '_col_0' [i64]
        [
                1
                0
                1
        ]
        ```

    """

    reference_texts: t.Union[list[str], str]
    col_in_text: str
    col_out: str = "text_comparison"

    def setup(self, settings: Settings):
        if isinstance(self.reference_texts, str):
            self.reference_texts = [self.reference_texts]
        return self

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        results = data.get_column(self.col_in_text).apply(
            lambda x: int(sum([x == y for y in self.reference_texts]))
        )
        return {"output": data.with_columns([results.alias(self.col_out)])}


# Check if a Keyword exists in input text
@register_op
class KeywordDetector(ColumnOp):
    """
    Detect keywords in given text.
    
    Attributes:
        col_in_text: (str) The input text.
        keyword: (str) The keywords to be checked.
        col_out: str = "keyword_detector"


    
    """
    col_in_text: str
    keyword: str
    col_out: str = "keyword_detector"

    def setup(self, settings: Settings):
        return self

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        results = data.get_column(self.col_in_text).apply(
            lambda sql: self.keyword in sql
        )
        return {"output": data.with_columns([results.alias(self.col_out)])}


# -----------------------------------------------------------
# Utility routines (for above operators)
# -----------------------------------------------------------


def extract_links(text, base_domain=None):
    """
    Extracts links from the given text.

    Args:
        text (str): The text from which links are to be extracted.
        base_domain (str, optional): If provided, only links containing this base domain will be returned. Defaults to None.

    Returns:
        list: A list of extracted links from the text, optionally filtered by the base domain.

    """
    pattern = r"\bhttps?://\S+\b"
    matches = re.findall(pattern, text)
    if base_domain is not None:
        return [m for m in matches if base_domain in m]
    else:
        return matches


def extract_version(url):
    """
    Extracts version information from the given URL.

    Attributes:
        url (str): The URL from which version information is to be extracted.

    Returns:
        str or None: The extracted version information, or None if no version information is found.

    """
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
