from uptrain.v0.core.classes.measurables import (
    Measurable,
    InputFeatureMeasurable,
    OutputFeatureMeasurable,
    FeatureMeasurable,
    FeatureConcatMeasurable,
    ConditionMeasurable,
    CustomMeasurable,
    AccuracyMeasurable,
    MAEMeasurable,
    MAPEMeasurable,
    ScalarFromEmbeddingMeasurable,
    DistanceMeasurable,
    RecHitRateMeasurable,
)
from uptrain.v0.ee.classes.measurables import (
    GrammerScoreMeasurable,
)

from uptrain.v0.constants import MeasurableType


class MeasurableResolver:
    """Class that resolves a measurable key to a measurable class instance."""

    def __init__(self, args) -> None:
        super().__init__()
        self._args = args

    def has_valid_resolve_args(self) -> bool:
        if self._args is None:
            return False
        if len(self._args) == 0:
            return False
        return True

    def resolve(self, framework) -> Measurable:
        if not self.has_valid_resolve_args():
            return None

        resolve_args = self._args
        measurable_type = resolve_args["type"]
        if measurable_type == MeasurableType.INPUT_FEATURE:
            return InputFeatureMeasurable(framework, resolve_args["feature_name"])
        elif measurable_type == MeasurableType.FEATURE_CONCAT:
            return FeatureConcatMeasurable(framework, resolve_args["feat_name_list"])
        elif measurable_type == MeasurableType.PREDICTION:
            return OutputFeatureMeasurable(framework)
        elif measurable_type == MeasurableType.CUSTOM:
            return CustomMeasurable(framework, resolve_args)
        elif measurable_type == MeasurableType.ACCURACY:
            return AccuracyMeasurable(framework)
        elif measurable_type == MeasurableType.MAE:
            return MAEMeasurable(framework)
        elif measurable_type == MeasurableType.MAPE:
            return MAPEMeasurable(framework)
        elif measurable_type == MeasurableType.CONDITION_ON_INPUT:
            return ConditionMeasurable(
                framework,
                InputFeatureMeasurable(framework, resolve_args["feature_name"]),
                resolve_args["condition_args"],
            )
        elif measurable_type == MeasurableType.CONDITION_ON_PREDICTION:
            return ConditionMeasurable(
                framework,
                OutputFeatureMeasurable(framework),
                resolve_args["condition_args"],
            )
        elif measurable_type == MeasurableType.SCALAR_FROM_EMBEDDING:
            return ScalarFromEmbeddingMeasurable(
                framework, resolve_args["idx"], resolve_args["extract_from"]
            )
        elif measurable_type == MeasurableType.DISTANCE:
            return DistanceMeasurable(
                framework,
                resolve_args["base"],
                resolve_args["reference"],
                resolve_args["distance_types"],
            )
        elif measurable_type == MeasurableType.REC_HIT_RATE:
            return RecHitRateMeasurable(framework)
        elif measurable_type == MeasurableType.GRAMMAR_SCORE:
            return GrammerScoreMeasurable(
                framework, resolve_args.get("feature_name", None)
            )
        else:
            raise Exception("Resolver not defined")
