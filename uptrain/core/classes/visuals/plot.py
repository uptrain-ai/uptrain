from typing import Any, Dict

from uptrain.core.classes.visuals import AbstractVisual
from uptrain.constants import PlotType, Visual


class Plot(AbstractVisual):
    visual_type = Visual.PLOT

    def base_init(self, framework, check: Dict[str, Any]) -> None:
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
            self._chart = self._line_chart

            if self.x_feature_name is None and self.y_feature_name is None:
                raise Exception(
                    "Both x_feature_name and y_feature_name are None - atleast one must be not None"
                )
        else:
            raise Exception("Plot Type is not supported")

    def base_check(self, inputs, outputs, gts=None, extra_args={}) -> None:
        self._chart(inputs, outputs, gts, extra_args)

    def _bar_chart(self, inputs, outputs, gts=None, extra_args={}) -> None:
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
        x_features = (
            list(range(length))
            if self.x_feature_name is None
            else inputs[self.x_feature_name]
        )
        y_features = (
            list(range(length))
            if self.y_feature_name is None
            else inputs[self.y_feature_name]
        )
        bars = inputs["bars"]
        data = {bar: {} for bar in bars}
        for i in range(length):
            data[bars[i]].update({x_features[i]: y_features[i]})
        self.framework.log_handler.add_bar_graphs(
            plot_name=self.plot_name, data=data, dashboard_name=self.dashboard_name
        )

    def _line_chart(self, inputs, outputs, gts=None, extra_args={}) -> None:
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
        x_features = (
            list(range(length))
            if self.x_feature_name is None
            else inputs[self.x_feature_name]
        )
        y_features = (
            list(range(length))
            if self.y_feature_name is None
            else inputs[self.y_feature_name]
        )
        for i in range(length):
            self.framework.log_handler.add_scalars(
                plot_name=self.plot_name,
                dictn={"y_value": y_features[i]},
                count=x_features[i],
                dashboard_name=self.dashboard_name,
                file_name=f"{self.x_feature_name}_{self.y_feature_name}",
            )
