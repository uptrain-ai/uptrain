import numpy as np
import pytest

from uptrain.core.classes.measurables import (
    AccuracyMeasurable,
    MAEMeasurable,
    MAPEMeasurable,
)


@pytest.fixture
def accuracy_measurable():
    return AccuracyMeasurable("dummy_framework")

@pytest.fixture
def mae_measurable():
    return MAEMeasurable("dummy_framework")

@pytest.fixture
def mape_measurable():
    return MAPEMeasurable("dummy_framework")

def test_accuracy_measurable_compute_returns_expected_values(accuracy_measurable):
    """Test that the accuracy measurable computes the expected values."""
    inputs = None
    outputs = [1, 2, 3]
    gts = [1, 3, 3]
    expected_values = np.array([True, False, True])
    assert np.array_equal(
        accuracy_measurable._compute(inputs, outputs, gts), expected_values
    )

def test_mae_measurable_compute_returns_expected_values(mae_measurable):
    """Test that the MAE measurable computes the expected values."""
    inputs = None
    outputs = [1, 2, 3]
    gts = [1, 3, 3]
    expected_values = np.array([0, 1, 0])
    assert np.array_equal(
        mae_measurable._compute(inputs, outputs, gts), expected_values
    )

def test_mape_measurable_compute_returns_expected_values(mape_measurable):
    """Test that the MAPE measurable computes the expected values."""
    inputs = None
    outputs = [1, 2, 3]
    gts = [1, 3, 3]
    expected_values = np.array([0, 33.33333333, 0])
    assert np.allclose(mape_measurable._compute(inputs, outputs, gts), expected_values)
