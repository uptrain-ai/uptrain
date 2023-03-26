import numpy as np
import pytest

from uptrain.core.classes.algorithms.popularity_bias import PopularityBias


@pytest.fixture
def pb():
    sessions = [
        ['a', 'b', 'c'],
        ['a', 'b'],
        ['a', 'c'],
        ['b', 'c'],
        ['b', 'c'],
        ['b'],
        ['c'],
    ]
    pb = PopularityBias(sessions=sessions)
    return pb


def test_init(pb: PopularityBias):
    """Test that the PopularityBias object is initialized correctly.
    
    The test passes if the PopularityBias object is initialized correctly
    and the popularity map is estimated correctly.
    """

    assert len(pb.all_popularity) == 0

    expected_popmap = {
        'a': 0.230760,
        'b': 0.384610,
        'c': 0.384610,
    }
    keys = ['a', 'b', 'c']
    result = np.array([pb.pop_map[key] for key in keys])
    expected_result = np.array([expected_popmap[key] for key in keys])
    
    assert np.allclose(result, expected_result, rtol=1e-4)


def test_add_prediction(pb: PopularityBias):
    """Test that the PopularityBias object adds predictions correctly.
    
    The test passes if the PopularityBias object adds predictions correctly
    and the popularity scores are added correctly.
    """

    pb.add_prediction(['a', 'b'])
    pb.add_prediction(['b', 'c'])
    
    assert len(pb.all_popularity) == 4
    
    result = pb.all_popularity
    expected_result = [0.230760, 0.384610, 0.384610, 0.384610]
    
    assert np.allclose(result, expected_result, rtol=1e-4)
