from uptrain.core.classes.visuals import AbstractVisual
from uptrain.constants import Visual, Statistic
from uptrain.core.classes.measurables import MeasurableResolver
from uptrain.core.classes.distances import DistanceResolver


class Umap(AbstractVisual):
    visual_type = Visual.UMAP

    def __init__(self, fw, check):
        self.framework = fw
        self.log_handler = fw.log_handler
        self.log_handler.add_writer(self.dashboard_name)
        self.measurable = MeasurableResolver(check["measurable_args"]).resolve(fw)
        self.aggregate_measurable = MeasurableResolver(check["aggregate_args"]).resolve(fw)
        self.item_counts = {}
        self.feats_dictn = {}
        self.distances_dictn = {}
        self.count_checkpoints = check['count_checkpoints']
        self.distance_types = check['distance_types']
        self.dist_classes = [DistanceResolver().resolve(x) for x in self.distance_types]

    def get_data_for_umap(self, count):
        distribution_anomaly = list(filter(lambda x: x.anomaly_type == Statistic.DISTRIBUTION_STATS, self.framework.check_manager.statistics_to_check))[0]
        return distribution_anomaly.get_feats_for_clustering(count)

