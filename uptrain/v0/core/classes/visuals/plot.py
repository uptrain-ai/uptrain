from typing import Any, Dict

from uptrain.v0.core.classes.visuals import AbstractVisual
from uptrain.v0.constants import PlotType, Visual


class Plot(AbstractVisual):
    """Class to expose the plotting API."""

    visual_type = Visual.PLOT

    def base_init(self, framework, check: Dict[str, Any]) -> None:
        """Base init for the Plot class.
        
        Parameters
        ----------
        framework
            UpTrain Framework object
        check
            Configuration dictionary for the plot
            The dictionary must contain the following keys:
                plot: The type of plot to use. Must be one of the following:
                    uptrain.PlotType.BAR_CHART
                    uptrain.PlotType.LINE_CHART
                    uptrain.PlotType.HISTOGRAM
                plot_name: The name of the plot. Defaults to the plot type.
                dashboard_name: The name of the dashboard. Defaults to "Plot".
            
            If the plot type is uptrain.PlotType.BAR_CHART:
                x_feature_name: The name of the feature to use for the x-axis.
                y_feature_name: The name of the feature to use for the y-axis.
            
            If the plot type is uptrain.PlotType.LINE_CHART:
                x_feature_name: The name of the feature to use for the x-axis.
                y_feature_name: The name of the feature to use for the y-axis.
            
            If the plot type is uptrain.PlotType.HISTOGRAM:
                feature_name: The name of the feature to use for the histogram.
        """

        self.framework = framework
        self.plot = check["plot"]
        self.plot_name = check.get("plot_name", self.plot)
        self.dashboard_name = check.get("dashboard_name", "Plot")

        if self.plot == PlotType.BAR_CHART:
            self.x_feature_name = check.get("x_feature_name", None)
            self.y_feature_name = check.get("y_feature_name", None)
            self._chart = self._bar_chart

            if self.x_feature_name is None and self.y_feature_name is None:
                raise Exception(
                    "Both x_feature_name and y_feature_name are None - atleast one must be not None"
                )
        elif self.plot == PlotType.LINE_CHART:
            self.x_feature_name = check.get("x_feature_name", None)
            self.y_feature_name = check.get("y_feature_name", None)
            self.count = 0
            self._chart = self._line_chart

            if self.x_feature_name is None and self.y_feature_name is None:
                raise Exception(
                    "Both x_feature_name and y_feature_name are None - atleast one must be not None"
                )
        elif self.plot == PlotType.HISTOGRAM:
            self.feature_name = check.get("feature_name", None)
            self._chart = self._histogram_chart

            if self.feature_name is None:
                raise Exception("feature_name is None")
        else:
            raise Exception("Plot Type is not supported")

    def base_check(self, inputs, outputs, gts=None, extra_args={}) -> None:
        self._chart(inputs, outputs, gts, extra_args)

    def _bar_chart(self, inputs, outputs, gts=None, extra_args={}) -> None:
        """Function to plot a bar chart."""

        # Check if the provided inputs were for the bar chart
        # TODO: refactor and make the checks better
        if not (
            self.x_feature_name in inputs.keys() or self.y_feature_name in inputs.keys()
        ):
            return
        
        length = (
            len(inputs[self.x_feature_name])
            if self.x_feature_name is not None
            else len(inputs[self.y_feature_name])
        )
        
        if self.x_feature_name is None:
            x_features = list(range(self.count, self.count + length))
            self.count += length
        else:
            x_features = inputs[self.x_feature_name]
        if self.y_feature_name is None:
            y_features = list(range(self.count, self.count + length))
            self.count += length
        else:
            y_features = inputs[self.y_feature_name]
        
        bars = inputs["bars"]
        data = {bar: {} for bar in set(bars)}
        
        for i in range(length):
            data[bars[i]].update({x_features[i]: y_features[i]})
        self.framework.log_handler.add_bar_graphs(
            plot_name=self.plot_name, data=data, dashboard_name=self.dashboard_name
        )

    def _histogram_chart(self, inputs, outputs, gts=None, extra_args={}) -> None:
        """Function to plot a histogram chart."""

        # Check if the provided inputs were for the histogram chart
        # TODO: refactor and make the checks better
        if not (self.feature_name in inputs.keys()):
            return
        self.log_handler.add_histogram(
            plot_name=self.plot_name,
            data=inputs[self.feature_name],
            dashboard_name=self.dashboard_name,
            file_name=f"{self.plot_name}_{self.feature_name}",
        )

    def _line_chart(self, inputs, outputs, gts=None, extra_args={}) -> None:
        """Function to plot a line chart."""
        
        # Check if the provided inputs were for the line chart
        # TODO: refactor and make the checks better
        if not (
            self.x_feature_name in inputs.keys() or self.y_feature_name in inputs.keys()
        ):
            return
        
        length = (
            len(inputs[self.y_feature_name])
            if self.x_feature_name is None
            else len(inputs[self.x_feature_name])
        )
        
        if self.x_feature_name is None:
            x_features = list(range(self.count, self.count + length))
            self.count += length
        else:
            x_features = inputs[self.x_feature_name]
        if self.y_feature_name is None:
            y_features = list(range(self.count, self.count + length))
            self.count += length
        else:
            y_features = inputs[self.y_feature_name]
        
        y_feature_name = (
            f"y_{self.y_feature_name}" if self.y_feature_name is not None else "y_value"
        )
        
        for i in range(length):
            self.framework.log_handler.add_scalars(
                plot_name=self.plot_name,
                dictn={y_feature_name: y_features[i]},
                count=x_features[i],
                dashboard_name=self.dashboard_name,
                file_name=f"{self.plot_name}_{self.x_feature_name}_{self.y_feature_name}",
            )
