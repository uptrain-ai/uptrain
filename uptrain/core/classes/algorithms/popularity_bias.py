import collections

class PopularityBias:
    def __init__(self, sessions, k=10):
        self.k = k
        self.all_popularity = []

        # estimate popularity from sessions
        pop_map = collections.defaultdict(lambda : 0)
        num_interactions = 0
        for session in sessions:
            for event in session:
                pop_map[event] += 1
                num_interactions += 1

        # normalize popularity
        self.pop_map = {k:v/num_interactions for k,v in pop_map.items()}

    def add_prediction(self, y_pred):
        pop_one_pred = [self.pop_map.get(x, 0.0) for x in y_pred]
        self.all_popularity += pop_one_pred
