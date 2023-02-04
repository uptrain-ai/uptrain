class AbstractStatistic:
    statistic_type = None

    def check(self, inputs, outputs, gts=None, extra_args={}):
        raise Exception("Should be defined for each class")
