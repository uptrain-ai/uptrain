import shap
import pickle
from uptrain.core.classes.visuals import AbstractVisual
from uptrain.constants import Visual
import os

class Shap(AbstractVisual):
    visual_type = Visual.SHAP
    dashboard_name = "SHAP_explanation"

    def base_init(self, fw, check):
        self.model = check["model"]
        self.explainer_created = False

        filename = 'explainer.pkl'
        self.fileloc = os.path.join(fw.log_handler.st_log_folder, filename)

        fw.log_handler.add_st_metadata(
            {'path_all_data': fw.path_all_data,
            'shap_num_points': check.get("shap_num_points", 1000),
            'path_shap_file': self.fileloc})

    def base_check(self, inputs, outputs, gts=None, extra_args={}):
        if not self.explainer_created:
            explainer = shap.Explainer(self.model)
            file = open(self.fileloc, 'wb')
            pickle.dump(explainer, file)
            file.close()
            self.explainer_created = True

