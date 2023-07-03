"""
This module implements visualization operators for simple-checks in uptrain.

The module provides the `PlotlyChart` class, which allows generating various types of charts using Plotly. 
The supported chart types are line, scatter, bar, histogram, and table. The charts are created based on 
the input DataFrame.

"""

from __future__ import annotations
import typing as t

from loguru import logger
from pydantic import Field
import polars as pl

if t.TYPE_CHECKING:
    from uptrain.framework import Settings
from uptrain.operators.base import *
from uptrain.utilities import lazy_load_dep

px = lazy_load_dep("plotly.express", "plotly")


__all__ = ["PlotlyChart"]


@register_op
class PlotlyChart(OpBaseModel):
    """
    Operator to generate various types of charts using Plotly.

    Attributes:
        kind (str): The type of chart to generate. Supported values are "line", "scatter", "bar",
            "histogram", and "table".
        props (dict): Additional properties to pass to the Plotly chart constructor.
        title (str): The title of the chart.
        filter_on (list[str]): The names of columns to filter the chart data on.

    Returns:
        dict: A dictionary containing the chart object.

    Example:
        ```
        import polars as pl
        from uptrain.operators import PlotlyChart

        # Create a DataFrame
        df = pl.DataFrame({
            "x": [1, 2, 3, 4, 5],
            "y": [10, 20, 15, 25, 30]
        })

        # Create a line chart using the PlotlyChart class
        line_chart = PlotlyChart.Line(props={"x": "x", "y": "y"}, title="Line Chart")

        # Generate the line chart
        chart = line_chart.run(df)["extra"]["chart"]

        # Show the chart
        chart.show()
        ```

    """

    kind: t.Literal["line", "scatter", "bar", "histogram", "table"]
    props: dict = Field(default_factory=dict)
    title: str = ""
    filter_on: list[str] = Field(default_factory=list)

    def setup(self, settings: Settings):
        return self

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        if self.kind == "table":
            return {"output": None}
        else:
            chart = getattr(px, self.kind)(data.to_pandas(), **self.props)
            return {"output": None, "extra": {"chart": chart}}

    @classmethod
    def Line(cls, **kwargs) -> PlotlyChart:
        """PlotlyChart: Creates a line chart."""
        return cls(kind="line", **kwargs)

    @classmethod
    def Scatter(cls, **kwargs) -> PlotlyChart:
        """PlotlyChart: Creates a scatter plot."""
        return cls(kind="scatter", **kwargs)

    @classmethod
    def Bar(cls, **kwargs) -> PlotlyChart:
        """PlotlyChart: Creates a bar chart."""
        return cls(kind="bar", **kwargs)

    @classmethod
    def Histogram(cls, **kwargs) -> PlotlyChart:
        """PlotlyChart: Creates a histogram."""
        return cls(kind="histogram", **kwargs)

    @classmethod
    def Table(cls, **kwargs) -> PlotlyChart:
        """PlotlyChart: Display the static table."""
        return cls(kind="table", **kwargs)
