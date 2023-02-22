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
        self.allowed_model_values = [x['allowed_values'] for x in check['model_args']]
        self.num_model_options = sum([len(x) > 1 for x in self.allowed_model_values])
        self.children = []

        if self.num_model_options > 0:
            for m in self.allowed_model_values[0]:
                check_copy = copy.deepcopy(check)
                check_copy['model_args'][0]['allowed_values'] = [m]
                check_copy['model_args'].append(copy.deepcopy(check_copy['model_args'][0]))
                del check_copy['model_args'][0]
                self.children.append(Distance(fw, check_copy))
        else:
            self.log_handler = fw.log_handler
            self.measurable = MeasurableResolver(check["measurable_args"]).resolve(fw)
            self.aggregate_measurable = MeasurableResolver(check["aggregate_args"]).resolve(
                fw
            )
            self.count_measurable = MeasurableResolver(check["count_args"]).resolve(
                fw
            )
            self.feature_measurables = [
                MeasurableResolver(x).resolve(fw) for x in check["feature_args"]
            ]
            self.model_measurables = [
                MeasurableResolver(x).resolve(fw) for x in check["model_args"]
            ]
            self.model_names = [x.col_name() for x in self.model_measurables]
            self.feature_names = [x.col_name() for x in self.feature_measurables]
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
            all_models = [x.compute_and_log(
                inputs, outputs, gts=gts, extra=extra_args
            ) for x in self.model_measurables]
            all_features = [x.compute_and_log(
                inputs, outputs, gts=gts, extra=extra_args
            ) for x in self.feature_measurables]

            for idx in range(len(aggregate_ids)):
                is_model_invalid = sum([all_models[jdx][idx] not in self.allowed_model_values[jdx] for jdx in range(len(self.allowed_model_values))])
                if is_model_invalid:
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
                models = dict(zip(['model_' + x for x in self.model_names], [all_models[jdx][idx] for jdx in range(len(self.model_names))]))
                features = dict(zip(['feature_' + x for x in self.feature_names], [all_features[jdx][idx] for jdx in range(len(self.feature_names))]))
                for distance_type in self.distance_types:
                    plot_name = (
                        distance_type
                        + "_"
                        + str(self.reference)
                    )
                    self.log_handler.add_scalars(
                        self.dashboard_name + "_" + plot_name,
                        {'y_' + distance_type: this_distances[distance_type][0]},
                        this_item_count,
                        self.dashboard_name,
                        features = features,
                        models = models,
                        file_name = str(aggregate_ids[idx])
                    )