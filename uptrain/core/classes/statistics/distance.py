import copy

from uptrain.core.lib.helper_funcs import extract_data_points_from_batch
from uptrain.core.classes.statistics import AbstractStatistic
from uptrain.core.classes.distances import DistanceResolver
from uptrain.core.classes.measurables import MeasurableResolver
from uptrain.constants import Statistic


class Distance(AbstractStatistic):
    dashboard_name = "distance"
    anomaly_type = Statistic.DISTANCE

    def __init__(self, fw, check):
        self.allowed_model_values = check['model_args'].get('allowed_values', [])
        self.children = []

        if len(self.allowed_model_values) > 1:
            for m in self.allowed_model_values:
                check_copy = copy.deepcopy(check)
                check_copy['model_args']['allowed_values'] = [m]
                self.children.append(Distance(fw, check_copy))
        else:
            self.dashboard_name = self.dashboard_name + "_" + self.allowed_model_values[0]

            self.log_handler = fw.log_handler
            self.log_handler.add_writer(self.dashboard_name)
            self.measurable = MeasurableResolver(check["measurable_args"]).resolve(fw)
            self.aggregate_measurable = MeasurableResolver(check["aggregate_args"]).resolve(
                fw
            )
            self.count_measurable = MeasurableResolver(check["count_args"]).resolve(
                fw
            )
            self.feature_meaasurables = [
                MeasurableResolver(x).resolve(fw) for x in check["feature_args"]
            ]
            self.model_measurable = MeasurableResolver(check["model_args"]).resolve(
                fw
            )
            self.item_counts = {}
            self.feats_dictn = {}
            self.reference = check["reference"]
            self.distance_types = check["distance_types"]
            self.dist_classes = [DistanceResolver().resolve(x) for x in self.distance_types]

    def check(self, inputs, outputs=None, gts=None, extra_args={}):
        if len(self.children) > 0:
            [x.check(inputs, outputs, gts, extra_args) for x in self.children]
        else:
            vals = self.measurable.compute_and_log(
                inputs, outputs, gts=gts, extra=extra_args
            )
            aggregate_ids = self.aggregate_measurable.compute_and_log(
                inputs, outputs, gts=gts, extra=extra_args
            )
            counts = self.count_measurable.compute_and_log(
                inputs, outputs, gts=gts, extra=extra_args
            )
            models = self.model_measurable.compute_and_log(
                inputs, outputs, gts=gts, extra=extra_args
            )
            all_features = [x.compute_and_log(
                inputs, outputs, gts=gts, extra=extra_args
            ) for x in self.feature_meaasurables]

            for idx in range(len(aggregate_ids)):
                if models[idx] not in self.allowed_model_values:
                    continue

                this_val = extract_data_points_from_batch(vals, [idx])

                if aggregate_ids[idx] not in self.item_counts:
                    self.item_counts.update({aggregate_ids[idx]: 0})
                    self.feats_dictn.update({aggregate_ids[idx]: this_val})

                this_item_count_prev = self.item_counts[aggregate_ids[idx]]
                if this_item_count_prev == counts[idx]:
                    continue
                self.item_counts[aggregate_ids[idx]] = counts[idx]
                this_item_count = self.item_counts[aggregate_ids[idx]]

                this_distances = dict(
                    zip(
                        self.distance_types,
                        [
                            x.compute_distance(
                                this_val, self.feats_dictn[aggregate_ids[idx]]
                            )
                            for x in self.dist_classes
                        ],
                    )
                )
                if self.reference == "running_diff":
                    self.feats_dictn[aggregate_ids[idx]] = this_val
                for distance_type in self.distance_types:
                    plot_name = (
                        distance_type
                        + "_"
                        + str(self.reference)
                        # + self.measurable.col_name()
                        # + " "
                        # + self.aggregate_measurable.col_name()
                    )
                    self.log_handler.add_scalars(
                        self.dashboard_name + "_" + plot_name,
                        {str(aggregate_ids[idx]): this_distances[distance_type][0]},
                        this_item_count,
                        self.dashboard_name,
                    )