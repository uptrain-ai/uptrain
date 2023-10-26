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
from uptrain.utilities import lazy_load_dep, polars_to_pandas

px = lazy_load_dep("plotly.express", "plotly>=5.0.0")
ps = lazy_load_dep("plotly.subplots", "plotly>=5.0.0")

__all__ = [
    "BarChart",
    "LineChart",
    "ScatterPlot",
    "Histogram",
    "MultiPlot",
    "CustomPlotlyChart",
]


# Not to be used as an operator, only as a base class
class Chart(OpBaseModel):
    props: dict = Field(default_factory=dict)
    title: str = ""
    x: str = ""
    y: str = ""
    color: str = ""
    description: str = ""

    def setup(self, settings: Settings = None):
        self.props = self.props | {
            k: v
            for k, v in [
                ("x", self.x),
                ("y", self.y),
                ("color", self.color),
                ("title", self.title),
                ("description", self.description),
            ]
            if v
        }
        return self

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        chart = getattr(px, self.kind)(polars_to_pandas(data), **self.props)

        # Add annotation based on the description
        if self.description:
            chart.update_layout(
                annotations=[
                    dict(
                        text=self.description,
                        x=0.5,
                        y=-0.25,
                        xref="paper",
                        yref="paper",
                        showarrow=False,
                        align="center",
                    )
                ]
            )

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
        description (str): Add a description of the chart being created.
        
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
    description: str = ""
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
        description (str): Add a description of the chart being created.
        
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
    description: str = ""
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
        description (str): Add a description of the chart being created.
         
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
    description: str = ""
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
        description (str): Add a description of the chart being created.
        
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
    description: str = ""
    color: str = ""
    symbol: str = "circle"

    kind = "scatter"


@register_op
class Scatter3DPlot(Chart):
    """
    Operator to generate a 3D scatter chart.

    Attributes:
        props (dict): Additional properties to pass to the ScatterPlot constructor.
        title (str): The title of the chart.
        x (str): The name of the column to use for the x-axis.
        y (str): The name of the column to use for the y-axis.
        z (str): The name of the column to use for the z-axis.
        color (str): The name of the column to use for the color.
        description (str): Add a description of the chart being created.

    Returns:
        dict: A dictionary containing the chart object.

    Example:
        ```
        import polars as pl
        from uptrain.operators import ScatterPlot

        # Create a DataFrame
        df = pl.DataFrame({
            "x": [1, 2, 3, 4, 5],
            "y": [10, 20, 15, 25, 30],
            "z": [30, 40, 55, 65, 70],
        })

        # Create a scatter chart using the ScatterPlot class
        scatter_plot = Scatter3DPlot(x="x", y="y", z="z", title="Scatter 3D Plot")

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
    z: str = ""
    description: str = ""
    color: str = ""
    symbol: str = ""

    kind = "scatter_3d"

    def setup(self, settings: Settings = None):
        super(Scatter3DPlot, self).setup()

        self.props = self.props | {
            k: v
            for k, v in [
                ("z", self.z),
                ("symbol", self.symbol),
            ]
            if v
        }
        return self


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
        description (str): Add a description of the chart being created.
        
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
    description: str = ""
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
        description (str): Add a description of the chart being created. (supports upto 70 characters without overlapping on graph)
        
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
    description: str = ""
    charts: list

    kind = "multiplot"

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        if type(self.charts[0]) == dict:
            self.charts = [Chart(**chart).setup() for chart in self.charts]

        fig = ps.make_subplots(
            rows=1,
            cols=len(self.charts),
            shared_xaxes=True,
            shared_yaxes=True,
            horizontal_spacing=0.05,
            vertical_spacing=0.2,  # Adjust this value for spacing between graph and annotation
            subplot_titles=[chart.title for chart in self.charts],
        )

        annotation_single_height = (
            -0.1
        )  # Adjust this value for single-line annotation position
        annotation_multi_height = (
            -0.3
        )  # Adjust this value for multiline annotation position
        annotation_line_height = (
            -0.05
        )  # Adjust this value for multiline annotation spacing

        for idx, chart in enumerate(self.charts):
            plot = getattr(px, chart.kind)(polars_to_pandas(data), **chart.props)

            # Use only the first trace from the plot
            trace = plot.data[0]
            fig.add_trace(trace, row=1, col=idx + 1)

            # Break down description into segments of four words each for long descriptions
            words = chart.description.split()
            if len(words) > 12:
                description_lines = [words[i : i + 4] for i in range(0, len(words), 4)]
                multiline_description = "<br>".join(
                    " ".join(line) for line in description_lines
                )
                annotation_text = multiline_description
                annotation_height = annotation_multi_height
            else:
                annotation_text = chart.description
                annotation_height = annotation_single_height

            # Add annotation for the description
            annotation = dict(
                text=annotation_text,
                align="center",
                showarrow=False,
                xref=f"x{idx + 1}",
                yref="paper",
                x=0.5,
                y=annotation_height,
                font=dict(size=10),
            )
            fig.add_annotation(annotation)

        fig.update_layout(
            title_text=self.title,
            showlegend=False,
            width=800,
            height=400,
            margin=dict(t=100, b=50),  # Adjust the bottom margin to center the title
        )

        return {"output": None, "extra": {"chart": fig}}
