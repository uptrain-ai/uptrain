import collections

from typing import List


class PopularityBias:
    """A class to estimate item popularity bias from a set of sessions and add predictions to it."""

    def __init__(self, sessions: List[List[str]], k: int = 10) -> None:
        """
        Initializes the PopularityBias object and estimates item popularity from sessions.

        Parameters
        ----------
        sessions
            A list of sessions, where each session is a list of item IDs.
        k
            The number of recommendations to make. Defaults to 10.
        """

        self.k = k
        self.all_popularity = []

        # Estimate item popularity from sessions
        pop_map = collections.defaultdict(lambda: 0)
        num_interactions = 0

        for session in sessions:
            for event in session:
                pop_map[event] += 1
                num_interactions += 1

        # Normalize item popularity
        self.pop_map = {k: v / num_interactions for k, v in pop_map.items()}

    def add_prediction(self, prediction: List[str]) -> None:
        """
        Adds a prediction to the all_popularity list.

        Parameters
        ----------
        prediction
            A list of item IDs for a single prediction.
        """

        # Get popularity score for each item in the prediction and add it
        pop_one_pred = [self.pop_map.get(event, 0.0) for event in prediction]
        self.all_popularity += pop_one_pred
