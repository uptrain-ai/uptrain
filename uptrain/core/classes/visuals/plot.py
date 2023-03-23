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
        # TODO: handle if x_feature_name or y_feature_name is None
        for i in range(len(inputs[self.x_feature_name])):
            self.framework.log_handler.add_scalars(self.plot_name, {"y_value": inputs[self.y_feature_name][i]}, inputs[self.x_feature_name][i], self.dashboard_name)
