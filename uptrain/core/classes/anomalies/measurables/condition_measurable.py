from uptrain.core.classes.anomalies.measurables import Measurable, FeatureMeasurable


class ConditionMeasurable(Measurable):
    def __init__(self, framework, underlying, condition) -> None:
        super().__init__(framework)
        self.underlying = underlying
        self.condition = condition
        self.feature = FeatureMeasurable(
            framework, underlying["feature_name"], underlying["dictn_type"]
        )
        if "formulae" in condition:
            formulae = condition["formulae"]
            if (formulae == "leq") or (formulae == "<="):
                condition_func = lambda x: (x <= condition["threshold"])
            elif (formulae == "le") or (formulae == "<"):
                condition_func = lambda x: (x < condition["threshold"])
            elif (formulae == "geq") or (formulae == ">="):
                condition_func = lambda x: (x >= condition["threshold"])
            elif (formulae == "ge") or (formulae == ">"):
                condition_func = lambda x: (x > condition["threshold"])
            elif (formulae == "eq") or (formulae == "=="):
                condition_func = lambda x: (x == condition["threshold"])
            else:
                raise Exception("Condition Formulae %s is not supported" % formulae)
        elif "func" in condition:
            condition_func = condition["func"]
        else:
            raise Exception(
                "Either func or formulae should be defined to resolve condition"
            )
        self.condition_func = condition_func

    def _compute(self, inputs=None, outputs=None, gts=None, extra=None) -> any:
        return self.condition_func(
            self.feature._compute(inputs=inputs, outputs=outputs, gts=gts, extra=extra)
        )

    def col_name(self):
        return (
            "Measurable: Condition("
            + self.feature.col_name()
            + ","
            + str(self.condition)
            + ")"
        )
