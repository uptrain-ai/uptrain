import numpy as np
import pytest

from uptrain.core.classes.distances import CosineDistance, L2Distance, NormRatio


@pytest.fixture
def cosine_distance():
    return CosineDistance()


@pytest.fixture
def l2_distance():
    return L2Distance()


@pytest.fixture
def norm_ratio():
    return NormRatio()


def test_compute_distance_CosineDistance(cosine_distance):
    """Test the compute_distance method of the CosineDistance class.

    The test checks for the expected result of the method for input vectors `base`
    and `reference`. It also tests for the case when the input vectors have incompatible
    shapes.

    The test passes if the cosine distance between `base` and `reference` is equal to
    the expected result, and if the method raises an exception when the input vectors
    have incompatible shapes.
    """

    # Test for incompatible shapes
    with pytest.raises(Exception):
        cosine_distance.compute_distance([[1, 2, 3]], [[4, 5, 6], [7, 8, 9]])

    # Test for expected result
    base = [[1, 2, 3], [10, 20, 0]]
    reference = [[4, 5, 6], [12, 19, 0]]
    result = cosine_distance.compute_distance(base, reference)
    expected_result = np.array([0.025368, 0.004963])
    assert np.allclose(result, expected_result, rtol=1e-4)


def test_compute_distance_L2Distance(l2_distance):
    """Test the compute_distance method of the L2Distance class.

    The test checks for the expected result of the method for input vectors `base`
    and `reference`. It also tests for the case when the input vectors have incompatible
    shapes.

    The test passes if the L2 distance between `base` and `reference` is equal to
    the expected result, and if the method raises an exception when the input vectors
    have incompatible shapes.
    """

    # Test for incompatible shapes
    with pytest.raises(Exception):
        l2_distance.compute_distance([[1, 2]], [[4, 5, 6]])

    # Test for expected result
    base = [[1, 2, 3], [4, 5, 6]]
    reference = [[7, 8, 9], [10, 11, 12]]
    result = l2_distance.compute_distance(base, reference)
    expected_result = np.array([108, 108])
    assert np.allclose(result, expected_result, rtol=1e-6)


def test_compute_distance_NormRatio(norm_ratio):
    """Test the compute_distance method of the NormRatio class.

    The test checks for the expected result of the method for input vectors `base`
    and `reference`.

    The test passes if the norm ratio between `base` and `reference` is equal to
    the expected result.
    """

    # Test for expected result
    base = [[1, 2], [3, 4], [5, 6]]
    ref = [[2, 4], [6, 8], [10, 12]]
    result = norm_ratio.compute_distance(base, ref)
    expected_result = np.array([0.5, 0.5, 0.5])
    assert np.allclose(result, expected_result, rtol=1e-6)
