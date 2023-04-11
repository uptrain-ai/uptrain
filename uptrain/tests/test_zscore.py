import uptrain
import numpy as np

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm, zscore

# Generate 5000 SAT scores from a normal distribution with mean=1200 and std=200

def test_zscore():
    random_state = np.random.RandomState(seed=1337)
    mean = 1200
    std = 200
    num_samples = 5000
    sat_scores = random_state.normal(mean, std, num_samples)

    # Add some random outliers that are not normally distributed
    num_outliers = 250
    outlier_mean = 1500
    outlier_std = 200
    outliers = np.concatenate((
        random_state.uniform(0, 200, num_outliers//2),
        random_state.uniform(2000, 2500, num_outliers//2),
    ))
    outliers = np.concatenate((outliers, random_state.normal(outlier_mean, outlier_std, num_outliers-len(outliers))))

    # Add the outliers to the SAT scores
    sat_scores = np.concatenate((sat_scores, outliers))

    # shuffle the scores
    random_state.shuffle(sat_scores)

    # Calculate the z-scores for each SAT score
    z_scores = zscore(sat_scores)
    outliers = np.where(np.abs(z_scores) > 3)


    def plot_graph(drifts = None):
                
        plt.hist(sat_scores, bins=50, alpha=0.5, label='SAT scores')

        # Overlay the normal distribution with mean=1200 and std=200
        x = np.linspace(sat_scores.min(), sat_scores.max(), 1000)
        y = norm.pdf(x, mean, std) * num_samples * np.diff(plt.hist(sat_scores, bins=50)[1])[0]
        plt.plot(x, y, 'r', label='Normal distribution')

        # Add a legend and labels
        plt.legend()
        plt.xlabel('SAT score')
        plt.ylabel('Frequency')
        plt.title('Distribution of SAT scores with outliers')

        # Show the plot
        plt.show()
    
    cfg = {
        "checks": [{
            'type': uptrain.Monitor.DATA_INTEGRITY,
            'measurable_args': {
                'type': uptrain.MeasurableType.INPUT_FEATURE,
                'feature_name':'scores'
            },
            'integrity_type': 'z_score',
            'threshold':3,
        }
        ],
        "retraining_folder": "uptrain_smart_data_data_integrity",
        "logging_args": {"st_logging": True},
    }

    framework = uptrain.Framework(cfg)
    batch_size = 64
    size = len(sat_scores)

    for i in range(size//batch_size):
        inputs = {'scores': sat_scores[i*batch_size:(i+1)*batch_size]}
        ids = framework.log(inputs=inputs)
        gts = [0] * batch_size
        framework.log(identifiers=ids, gts=gts)

test_zscore()
