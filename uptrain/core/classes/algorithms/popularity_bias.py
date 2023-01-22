class PopularityBias:
    def __init__(self, rec_list, pop_map, k=10):
        self.k = k
        self.pop_map = pop_map
        self.rec_list = rec_list
        self.all_popularity = []

    def add_prediction(self, y_pred):
        y_preds = self.rec_list.sku_only(y_pred)[0]
        pop_one_pred = [self.pop_map.get(x, 0.0) for x in y_preds]
        self.all_popularity += pop_one_pred
