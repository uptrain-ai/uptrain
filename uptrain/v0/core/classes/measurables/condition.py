from typing import Any, Dict

from uptrain.v0.core.classes.measurables import Measurable, FeatureMeasurable


class ConditionMeasurable(Measurable):
    """Class that computes a boolean condition on a measurable feature."""

    def __init__(
        self, framework, underlying: Dict[str, Any], condition: Dict[str, Any]
    ) -> None:
        """Constructor for ConditionMeasurable class.

        Parameters
        ----------
        framework
            UpTrain Framework object
        underlying
            A dictionary containing the feature_name to apply the condition on and
            the dictn_type (whether to apply on inputs or outputs).
            dictn_type should be "inputs" for applying InputFeatureMeasurable
            dictn_type should be "outputs" for applying OutputFeatureMeasurable
        condition
            A dictionary containing either "formulae" or "func" as key.
            If "formulae" is provided:
                - it must be a boolean operator from the following list of operators:
                    ["<", "<=", ">", ">=", "==", "le", "leq", "ge", "geq", "eq"]
                - it must contain "threshold" as key which provides the value to perform
                  the boolean condition against.
            If "func" is provided, it should map to a callback that accepts a single
            argument and returns a boolean value.
        """
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

    def _compute(self, inputs=None, outputs=None, gts=None, extra=None) -> Any:
        return self.condition_func(
            self.feature._compute(inputs=inputs, outputs=outputs, gts=gts, extra=extra)
        )

    def col_name(self) -> str:
        return f"Condition({self.feature.col_name()}, {str(self.condition)})"
