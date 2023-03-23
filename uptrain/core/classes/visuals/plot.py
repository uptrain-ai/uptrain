from uptrain.core.classes.visuals import AbstractVisual
from uptrain.constants import PlotType, Visual


class Plot(AbstractVisual):
    visual_type = Visual.PLOT
    dashboard_name = "Plot"

    def base_init(self, framework, check) -> None:
        self.framework = framework
        self.plot = check["plot"]

        if self.plot == PlotType.LINE_CHART:
            x_feature_name = check.get('x_feature_name', None)
            y_feature_name = check.get('y_feature_name', None)

            if x_feature_name is None and y_feature_name is None:
                raise Exception("Both x_feature_name and y_feature_name are None - atleast one must be not None")
        else:
            raise Exception("Plot Type is not supported")
    
    def base_check(self, inputs, outputs, gts=None, extra_args={}) -> None:
        pass
