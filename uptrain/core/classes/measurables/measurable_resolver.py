from uptrain.core.classes.measurables import (
    Measurable,
    FeatureMeasurable,
    ConditionMeasurable,
    CustomMeasurable,
    AccuracyMeasurable,
    MAEMeasurable,
    MAPEMeasurable,
    ScalarFromEmbeddingMeasurable,
    DistanceMeasurable,
    RecHitRateMeasurable,
)
from uptrain.constants import MeasurableType


class MeasurableResolver:
    def __init__(self, args) -> None:
        super().__init__()
        self._args = args

    def has_valid_resolve_args(self):
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
            return FeatureMeasurable(framework, resolve_args["feature_name"], "inputs")
        elif measurable_type == MeasurableType.PREDICTION:
            return FeatureMeasurable(framework, resolve_args["feature_name"], "outputs")
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
                FeatureMeasurable(framework, resolve_args["feature_name"], "inputs"),
                resolve_args["condition_args"],
            )
        elif measurable_type == MeasurableType.CONDITION_ON_PREDICTION:
            return ConditionMeasurable(
                framework,
                FeatureMeasurable(framework, resolve_args["feature_name"], "outputs"),
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
        else:
            raise Exception("Resolver not defined")
