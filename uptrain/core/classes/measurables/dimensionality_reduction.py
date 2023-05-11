from typing import Optional, Union, TYPE_CHECKING

try:
    import umap
except:
    umap = None
import numpy as np
from sklearn.manifold import TSNE

from uptrain.constants import Visual
from uptrain.core.lib.helper_funcs import dependency_required
from uptrain.core.classes.measurables import Measurable


@dependency_required(umap, "umap-learn")
class DimensionalityReductionMeasurable(Measurable):

    def __init__(self, fw, check):
        self.framework = fw
        self.dim = check.get("dim", "2D")

        self.total_count = 0
        self.prev_calc_at = 0
        self.vals = []
        self.visual_type = check.get("visual_type", Visual.UMAP)
        if self.visual_type == Visual.UMAP:
            self.umap_init(check)
        elif self.visual_type == Visual.TSNE:
            self.tsne_init(check)
        else:
            raise ValueError(f"Unknown visual type {self.visual_type}")

    def umap_init(self, check):
        self.min_dist = check.get("min_dist", 0.01)
        self.n_neighbors = check.get("n_neighbors", 20)
        self.metric_umap = check.get("metric", "euclidean")

    def tsne_init(self, check):
        self.perplexity = check.get("perplexity", 30.0)
        self.early_exaggeration = check.get("early_exaggeration", 12.0)
        self.learning_rate = check.get("learning_rate", "auto")
        self.n_iter = check.get("n_iter", 1000)
        self.n_iter_without_progress = check.get("n_iter_without_progress", 300)
        self.min_grad_norm = check.get("min_grad_norm", 1e-7)
        self.metric_tsne = check.get("metric", "euclidean")
        self.metric_params = check.get("metric_params", None)
        self.init = check.get("init", "pca")
        self.verbose = check.get("verbose", 0)
        self.random_state = check.get("random_state", None)
        self.method = check.get("method", "barnes_hut")
        self.angle = check.get("angle", 0.5)
        self.n_jobs = check.get("n_jobs", None)
        self.vals = []

    def _compute(self, inputs, outputs, gts=None, extra=None):

        vals = inputs["emb_data"]
        self.vals.extend(vals)
        emb_list = np.array(self.vals)

        if emb_list.shape[0] > 10:
            umap_list = self.get_embs_and_clusters(emb_list)
        return umap_list

    def get_embs_and_clusters(self, emb_list):
        if self.dim == "2D":
            n_components = 2
        else:
            n_components = 3

        if self.visual_type == Visual.UMAP:
            compressed_embeddings = umap.UMAP(
                n_neighbors=self.n_neighbors,
                n_components=n_components,
                min_dist=self.min_dist,
                metric=self.metric_umap,
            ).fit_transform(emb_list)
        elif self.visual_type == Visual.TSNE:
            compressed_embeddings = TSNE(
                n_components=n_components,
                perplexity=self.perplexity,
                early_exaggeration=self.early_exaggeration,
                learning_rate=self.learning_rate,
                n_iter=self.n_iter,
                n_iter_without_progress=self.n_iter_without_progress,
                min_grad_norm=self.min_grad_norm,
                metric=self.metric_tsne,
                init=self.init,
                verbose=self.verbose,
                random_state=self.random_state,
                method=self.method,
                angle=self.angle,
                n_jobs=self.n_jobs,
            ).fit_transform(emb_list)

        return compressed_embeddings