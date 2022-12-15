from oodles.core.classes.anomalies import AbstractAnomaly
from oodles.core.classes.algorithms import PopularityBias
from oodles.constants import BiasAlgo


class RecommendationBias(AbstractAnomaly):
    dashboard_name = 'pop_bias'

    def __init__(self, check, log_args={}):
        super().__init__(log_args=log_args)
        self.acc_arr = []
        if check["algorithm"] == BiasAlgo.POPULARITY_BIAS:
            rec_list = check.get("rec_list", None)
            pop_map = check.get("pop_map", None)
            self.algo = PopularityBias(rec_list, pop_map)
        else:
            raise Exception("Recommendation bias type not supported")

    def need_ground_truth(self):
        return False

    def check(self, inputs, outputs, gts=None, extra_args={}):
        y_pred = outputs[0]
        self.algo.add_prediction(y_pred)
        pop_arr = self.algo.all_popularity
        self.plot_histogram('Pupolarity Bias', pop_arr, len(pop_arr))

    def is_data_interesting(self, inputs, outputs, gts=None, extra_args={}):
        return False