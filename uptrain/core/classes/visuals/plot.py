from typing import Any, Dict

from uptrain.core.classes.visuals import AbstractVisual
from uptrain.constants import PlotType, Visual


class Plot(AbstractVisual):
    visual_type = Visual.PLOT
    dashboard_name = "Plot"

    def base_init(self, framework, check: Dict[str, Any]) -> None:
        self.framework = framework
        self.plot = check["plot"]
        self.plot_name = check.get("plot_name", "Plot")

        if self.plot == PlotType.LINE_CHART:
            self.x_feature_name = check.get('x_feature_name', None)
            self.y_feature_name = check.get('y_feature_name', None)

            if self.x_feature_name is None and self.y_feature_name is None:
                raise Exception("Both x_feature_name and y_feature_name are None - atleast one must be not None")
        else:
            raise Exception("Plot Type is not supported")
    
    def base_check(self, inputs, outputs, gts=None, extra_args={}) -> None:
        if self.plot == PlotType.LINE_CHART:
            self._line_chart(inputs, outputs, gts, extra_args)
    
    def _line_chart(self, inputs, outputs, gts=None, extra_args={}) -> None:
        if self.x_feature_name is None:
            for i in range(len(inputs[self.y_feature_name])):
                self.framework.log_handler.add_scalars(plot_name = self.plot_name, dictn = {"y_value": inputs[self.y_feature_name][i]}, count = i, dashboard_name = self.dashboard_name, file_name = self.y_feature_name)
        elif self.y_feature_name is None:
            for i in range(len(inputs[self.x_feature_name])):
                self.framework.log_handler.add_scalars(plot_name = self.plot_name, dictn = {"x_value": i}, count = inputs[self.x_feature_name][i], dashboard_name = self.dashboard_name, file_name = self.x_feature_name)
        else:
            for i in range(len(inputs[self.x_feature_name])):
                self.framework.log_handler.add_scalars(plot_name = self.plot_name, dictn = {"y_value": inputs[self.y_feature_name][i]}, count = inputs[self.x_feature_name][i], dashboard_name = self.dashboard_name, file_name = f'{self.x_feature_name}_{self.y_feature_name}')
