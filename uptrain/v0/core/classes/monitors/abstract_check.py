import copy
from abc import ABC
import os

from uptrain.v0.core.classes.measurables import MeasurableResolver

class AbstractCheck(ABC):

    def __init__(self, fw, check) -> None:
        super().__init__()
        self.log_handler = fw.log_handler
        self.dashboard_name = check["type"]
        self.measurable = MeasurableResolver(check.get("measurable_args", None)).resolve(fw)

        self.feature_measurables = [
            MeasurableResolver(x).resolve(fw) for x in check.get("feature_args", [])
        ]
        self.feature_names = [x.col_name() for x in self.feature_measurables]

        self.model_measurables = [
            MeasurableResolver(x).resolve(fw) for x in check.get("model_args", [])
        ]
        self.model_names = [x.col_name() for x in self.model_measurables]

        all_choices = self.model_choices(check)
        self.children = []
        if len(all_choices) > 1:
            for choice in all_choices:
                check_copy = copy.deepcopy(check)
                check_copy.update(choice)
                self.children.append(self.__class__(fw, check_copy))
        else:
            self.base_init(fw, check)

        if check.get("feat_slicing", False):
            self.path_dashboard_data = os.path.join(fw.fold_name, f"{self.dashboard_name}.csv")
            fw.log_handler.add_dashboard_metadata(
            {
                'feat_slicing': True,
                'path_all_data': fw.path_all_data,
                'feat_name_list': fw.feat_name_list,
                'path_dashboard_data': self.path_dashboard_data,
            },
            self.dashboard_name,)

    def base_init(self, fw, check):
        print(self.__class__)
        raise Exception("Should be defined for each class")

    def model_choices(self, check):
        allowed_model_values = [x['allowed_values'] for x in check.get('model_args', [])]
        num_model_options = sum([len(x) > 1 for x in allowed_model_values])

        all_choices = []
        if num_model_options > 0:
            for m in allowed_model_values[0]:
                check_copy = copy.deepcopy(check)
                check_copy['model_args'][0]['allowed_values'] = [m]
                check_copy['model_args'].append(copy.deepcopy(check_copy['model_args'][0]))
                del check_copy['model_args'][0]
                all_choices.extend(self.model_choices(check_copy))
            return all_choices
        else:
            self.allowed_model_values = [x['allowed_values'] for x in check.get('model_args', [])]
            return [{"model_args": check.get("model_args", [])}]

    def check(self, inputs, outputs, gts=None, extra_args={}):
        if len(self.children) > 0:
            [x.check(inputs, outputs, gts=gts, extra_args=extra_args) for x in self.children]
        else:
            self.base_check(inputs, outputs, gts=gts, extra_args=extra_args)

    def base_check(self, inputs, outputs, gts=None, extra_args={}):
        print(self.__class__)
        raise Exception("Should be defined for each class")