"""
This module implements visualization operators for checks in uptrain.

The module provides the `BarChart`, `LineChart`, `ScatterPlot`, `Table`, `Histogram`, and `MultiPlot` classes, 
which allow generating various types of visualizations. The charts are created based on 
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
ps = lazy_load_dep("plotly.subplots", "plotly")

__all__ = ["BarChart", "LineChart", "ScatterPlot", "Histogram", "MultiPlot", "CustomPlotlyChart"]


# Not to be used as an operator, only as a base class
class Chart(OpBaseModel):
    props: dict = Field(default_factory=dict)
    title: str = ""
    x: str = ""
    y: str = ""
    color: str = ""

    def setup(self, settings: Settings = None):
        self.props = self.props | {k: v for k, v in [("x", self.x), ("y", self.y), ("color", self.color), ("title", self.title)] if v}
        return self
    
    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        chart = getattr(px, self.kind)(data.to_pandas(), **self.props)
        return {"output": None, "extra": {"chart": chart}}


@register_op
class CustomPlotlyChart(Chart):
    """
    Operator to generate a custom plotly chart, other than the ones provided by uptrain.

    Attributes:
        props (dict): Additional properties to pass to the PlotlyChart constructor.
        title (str): The title of the chart.
        x (str): The name of the column to use for the x-axis.
        y (str): The name of the column to use for the y-axis.
        color (str): The name of the column to use for the color.
        kind (str): The type of chart to generate.

    Returns:
        dict: A dictionary containing the chart object.

    Example:
        ```
        import polars as pl
        from uptrain.operators import CustomPlotlyChart

        # Create a DataFrame
        df = pl.DataFrame({
            "x": [1, 2, 3, 4, 5],
            "y": [10, 20, 15, 25, 30]
        })

        # Create a funnel chart using the CustomPlotlyChart class
        funnel_chart = CustomPlotlyChart(x="x", y="y", title="Funnel Chart")

        # Generate the funnel chart
        chart = funnel_chart.run(df)["extra"]["chart"]

        # Show the chart
        chart.show()
        ```

    """

    props: dict = Field(default_factory=dict)
    title: str = ""
    x: str = ""
    y: str = ""
    color: str = ""
    kind: str = Field(default_factory=str)


@register_op
class BarChart(Chart):
    """
    Operator to generate a bar chart.

    Attributes:
        props (dict): Additional properties to pass to the BarChart constructor.
        x (str): The name of the column to use for the x-axis.
        y (str): The name of the column to use for the y-axis.
        color (str): The name of the column to use for the color.
        barmode (str): The type of bar chart to generate.
        title (str): The title of the chart.

    Returns:
        dict: A dictionary containing the chart object.

    Example:
        ```
        import polars as pl
        from uptrain.operators import BarChart

        # Create a DataFrame
        df = pl.DataFrame({
            "x": [1, 2, 3, 4, 5],
            "y": [10, 20, 15, 25, 30]
        })

        # Create a bar chart using the BarChart class
        bar_chart = BarChart(x="x", y="y", title="Bar Chart")

        # Generate the bar chart
        chart = bar_chart.run(df)["extra"]["chart"]

        # Show the chart
        chart.show()
        ```

    """


    props: dict = Field(default_factory=dict)
    title: str = ""
    x: str = ""
    y: str = ""
    color: str = ""
    barmode: str = "group"

    kind = "bar"


@register_op
class LineChart(Chart):
    """
    Operator to generate a line chart.

    Attributes:
        props (dict): Additional properties to pass to the LineChart constructor.
        x (str): The name of the column to use for the x-axis.
        y (str): The name of the column to use for the y-axis.
        color (str): The name of the column to use for the color.
        title (str): The title of the chart.

    Returns:
        dict: A dictionary containing the chart object.

    Example:
        ```
        import polars as pl
        from uptrain.operators import LineChart

        # Create a DataFrame
        df = pl.DataFrame({
            "x": [1, 2, 3, 4, 5],
            "y": [10, 20, 15, 25, 30]
        })

        # Create a line chart using the LineChart class
        line_chart = LineChart(x="x", y="y", title="Line Chart")

        # Generate the line chart
        chart = line_chart.run(df)["extra"]["chart"]

        # Show the chart
        chart.show()
        ```

    """


    props: dict = Field(default_factory=dict)
    title: str = ""
    x: str = ""
    y: str = ""
    color: str = ""

    kind = "line"


@register_op
class ScatterPlot(Chart):
    """
    Operator to generate a scatter chart.

    Attributes:
        props (dict): Additional properties to pass to the ScatterPlot constructor.
        title (str): The title of the chart.
        x (str): The name of the column to use for the x-axis.
        y (str): The name of the column to use for the y-axis.
        color (str): The name of the column to use for the color.

    Returns:
        dict: A dictionary containing the chart object.

    Example:
        ```
        import polars as pl
        from uptrain.operators import ScatterPlot

        # Create a DataFrame
        df = pl.DataFrame({
            "x": [1, 2, 3, 4, 5],
            "y": [10, 20, 15, 25, 30]
        })

        # Create a scatter chart using the ScatterPlot class
        scatter_plot = ScatterPlot(x="x", y="y", title="Scatter Plot")

        # Generate the scatter plot
        chart = scatter_plot.run(df)["extra"]["chart"]

        # Show the chart
        chart.show()
        ```

    """


    props: dict = Field(default_factory=dict)
    title: str = ""
    x: str = ""
    y: str = ""
    color: str = ""
    symbol: str = "circle"

    kind = "scatter"


@register_op
class Histogram(Chart):
    """
    Operator to generate a histogram.

    Attributes:
        props (dict): Additional properties to pass to the Histogram chart constructor.
        title (str): The title of the chart.
        x (str): The name of the column to use for the x-axis.
        y (str): The name of the column to use for the y-axis.
        color (str): The name of the column to use for the color.
        nbins (int): The maximum number of bins to use for the histogram.

    Returns:
        dict: A dictionary containing the chart object.

    Example:
        ```
        import polars as pl
        from uptrain.operators import Histogram

        # Create a DataFrame
        df = pl.DataFrame({
            "x": [1, 2, 3, 4, 5],
            "y": [10, 20, 15, 25, 30]
        })

        # Create a histogram chart using the Histogram class
        histogram_chart = Histogram(x="x", y="y", title="Histogram Chart")

        # Generate the histogram chart
        chart = histogram_chart.run(df)["extra"]["chart"]

        # Show the chart
        chart.show()
        ```

    """


    props: dict = Field(default_factory=dict)
    title: str = ""
    x: str = ""
    y: str = ""
    color: str = ""
    nbins: int = 20

    kind = "histogram"


@register_op
class MultiPlot(Chart):
    """
    Operator to generate a subplot that can display multiple charts side-by-side.

    Attributes:
        props (dict): Additional properties to pass to the MultiPlot constructor.
        title (str): The title of the chart.
        charts (list): A list of charts to display in the subplot.

    Returns:
        dict: A dictionary containing the chart object.

    Example:
        ```
        import polars as pl
        from uptrain.operators import MultiPlot, LineChart, ScatterPlot, BarChart, Histogram

        # Create a DataFrame
        df = pl.DataFrame({
            "x": [1, 2, 3, 4, 5],
            "y": [10, 20, 15, 25, 30]
        })

        # Create a multiplot using the MultiPlot class
        multiplot = MultiPlot(
            props={},
            charts=[
                LineChart(
                    x="x",
                    y="y", 
                    title="Line Chart"
                ),
                ScatterPlot(
                    x="x",
                    y="y",
                    title="Scatter Plot"
                ),
                BarChart(
                    x="x",
                    y="y",
                    title="Bar Chart"
                ),
                Histogram(
                    x="x",
                    y="y",
                    title="Histogram"
                )
            ],
            title="MultiPlot",
        )

        # Generate the multiplot
        chart = multiplot.run(df)["extra"]["chart"]

        # Show the chart
        chart.show()
        ```

    """

    props: dict = Field(default_factory=dict)
    title: str = ""
    charts: list

    kind = "multiplot"

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        if type(self.charts[0]) == dict:
            self.charts = [Chart(**chart).setup() for chart in self.charts]
        subplot = ps.make_subplots(
            rows=1,
            cols=len(self.charts),
            subplot_titles=[chart.title for chart in self.charts],
        )

        for chart in self.charts:
            plot = getattr(px, chart.kind)(data.to_pandas(), **chart.props)
            subplot.add_trace(plot.to_dict()["data"][0], row=1, col=self.charts.index(chart) + 1)

        subplot.update_layout(title_text=self.title)
        return {"output": None, "extra": {"chart": subplot}}

