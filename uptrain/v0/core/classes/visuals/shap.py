import os
import pickle

try:
    import shap
except:
    shap = None

from uptrain.v0.core.classes.visuals import AbstractVisual
from uptrain.v0.constants import Visual
from uptrain.v0.core.lib.helper_funcs import dependency_required


@dependency_required(shap, "shap")
class Shap(AbstractVisual):
    visual_type = Visual.SHAP
    dashboard_name = "SHAP_explanation"

    def base_init(self, fw, check):
        self.model = check["model"]
        self.explainer_created = False

        filename = "explainer.pkl"
        self.fileloc = os.path.join(fw.log_handler.st_log_folder, filename)
        feat_name_list = check.get("feat_name_list", fw.feat_name_list)

        fw.log_handler.add_st_metadata(
            {
                "path_all_data": fw.path_all_data,
                "feat_name_list": feat_name_list,
                "shap_num_points": check.get("shap_num_points", 1000),
                "path_shap_file": self.fileloc,
            }
        )

    def base_check(self, inputs, outputs, gts=None, extra_args={}):
        if not self.explainer_created:
            explainer = shap.Explainer(self.model)
            file = open(self.fileloc, "wb")
            pickle.dump(explainer, file)
            file.close()
            self.explainer_created = True
