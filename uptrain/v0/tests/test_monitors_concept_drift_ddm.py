import numpy as np
import string
import uptrain.v0 as v0


def test_concept_drift_ddm():
    """Test concept drift detection using DDM algorithm.

    We generate a synthetic dataset consisting of 1000 strings, each of length
    between 10 to 20 characters, containing lowercase alphabets, digits, and
    spaces. We also generate a binary sentiment label for each string. A label
    of 0 means that the sentiment is negative, and a label of 1 means that the
    sentiment is positive.

    Note that you can use a real dataset as well. However, for the sake of
    simplicity, we use a synthetic dataset to demonstrate how DDM works.

    Assume that we have a model that has been trained to predict the sentiment
    of a sentence. It performs well for the most part but occasionally makes
    incorrect predictions. However, for some reason, it starts to perform poorly
    on some newer data. How do we detect this?

    We use the DDM algorithm to detect the concept drift. The drift will arise
    somewhere around the 800th sentence.

    To introduce concept drift to our synthetic dataset, we randomly flip the
    predictions of 10% of the strings. This simulates a scenario where the model
    makes incorrect predictions on some data. We also deliberately make the last
    20% of predictions random. This simulates a scenario where the model encounters
    new or unseen data, causing the predictions to become inaccurate.

    In this test, we use the UpTrain framework to log the inputs, outputs, and ground
    truths. We set up the framework to use the DDM algorithm to monitor the error rate
    of the model. The error rate is calculated as the binary accuracy between the
    predictions and the ground truths. We set the threshold for warning to 2.0, and
    drift to 3.0. This means that if the error rate crosses 2.0, the model has
    begun to perform poorly on some data. If the error rate crosses 3.0, a concept
    drift alert will be raised. This means that the model is performing really poorly
    and is inaccurate on some recent data that it has been exposed to.

    The test passes if the DDM algorithm successfully detects the concept drift and
    raises an alert around the point where the predictions start becoming inaccurate.
    """

    random_state = np.random.RandomState(seed=1337)
    alphabet = np.array(list(map(ord, string.ascii_lowercase + string.digits + " ")))

    def random_sentence(length):
        """Generate a random sentence of given length"""
        return "".join(list(map(chr, random_state.choice(alphabet, size=length))))

    n = 1000
    inputs = np.array([random_sentence(random_state.randint(10, 20)) for _ in range(n)])
    sentiments = np.array([random_state.choice([0, 1]) for _ in range(n)])
    predictions = sentiments.copy()

    # Make 10% predictions incorrect randomly, i.e., if a sentiment is correctly classified,
    # make it incorrectly classified and vice versa
    incorrect_predictions = random_state.choice(n, size=int(n * 0.1), replace=False)
    predictions[incorrect_predictions] = 1 - predictions[incorrect_predictions]

    # Deliberately make the last 20% of predictions random
    random_predictions = np.arange(n - int(n * 0.2), n)
    predictions[random_predictions] = random_state.choice(
        [0, 1], size=len(random_predictions)
    )

    # Create a configuration for the framework
    cfg = {
        # Define checks to be performed
        "checks": [
            # Check: Concept drift detection using DDM algorithm
            # with accuracy as the measurable for the feature "data"
            {
                "type": v0.Monitor.CONCEPT_DRIFT,
                "algorithm": v0.DataDriftAlgo.DDM,
                "measurable_args": {"type": v0.MeasurableType.ACCURACY},
                "warm_start": 200,
                "warn_threshold": 2.0,
                "alarm_threshold": 3.0,
            }
        ],
        # Specify where the logging data should be stored
        "retraining_folder": "uptraining_smart_data_concept_drift_ddm",
        # Specify logging arguments
        # "st_logging" should be True if we want streamlit logging, False otherwise
        "logging_args": {"st_logging": True},
    }

    framework = v0.Framework(cfg)
    batch_size = 64

    # Feed the data to the framework
    for i in range(n // batch_size):
        input = {"data": inputs[i * batch_size : (i + 1) * batch_size]}
        output = predictions[i * batch_size : (i + 1) * batch_size]
        gts = sentiments[i * batch_size : (i + 1) * batch_size]
        ids = framework.log(inputs=input, outputs=output)
        framework.log(identifiers=ids, gts=gts)
