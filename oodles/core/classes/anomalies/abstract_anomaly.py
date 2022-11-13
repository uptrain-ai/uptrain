class AbstractAnomaly:
    def check(self, inputs, outputs, extra_args={}):
        raise Exception("Should be defined for each class")

    def is_data_interesting(self, inputs, outputs, extra_args={}):
        raise Exception("Should be defined for each class")