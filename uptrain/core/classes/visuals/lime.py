try:
    import lime
    LIME_PRESENT = True
except:
    LIME_PRESENT = False
from uptrain.core.classes.visuals import AbstractVisual
from uptrain.constants import Visual

class Lime(AbstractVisual):
    visual_type = Visual.LIME
    dashboard_name = "LIME_explanation"

    def base_init(self, fw, check):
        self.model = check["model"]
        self.explainer_created = False

    def base_check(self, fw, check):
        pass


