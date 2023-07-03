import os
import os
from uptrain.framework import CheckSet, Settings, Check
from uptrain.operators import (
    PlotlyChart,
    Distribution,
    CosineSimilarity,
    UMAP,
    SelectOp,
)
from uptrain.io import JsonReader, JsonWriter
from uptrain.operators.language import (
    Embedding,
    RougeScore,
    DocsLinkVersion,
    TextLength,
    TextComparison,
)

dataset = "examples/datasets/qna_on_docs_samples.jsonl"

def get_checkset(source_path):
    # Define the config
    checks = []

    checks.append(
        Check(
            name="distribution_of_document_embeddings",
            sequence=[
                Embedding(
                    model="MiniLM-L6-v2",
                    col_in_text="document_text",
                    col_out='response_embeddings'
                ),
                Distribution(
                    kind="cosine_similarity",
                    col_in_embs=["context_embeddings", "response_embeddings"],
                    col_in_groupby=["question_idx", "experiment_id"],
                    col_out=["similarity-context", "similarity-response"],
                ),
                Embedding(
                    model="MiniLM-L6-v2",
                    col_in_text="similarity-response"
                ),
            ],
            plot=[
                PlotlyChart.Histogram(
                    title="Embeddings similarity - Context",
                    props=dict(x="similarity-context", nbins=20),
                ),
                PlotlyChart.Histogram(
                    title="Embeddings similarity - Responses",
                    props=dict(x="similarity-response", nbins=20),
                ),
            ],
        )
    )

    checks.append(
        Check(
            name="text_overlap_between_documents",
            sequence=[
                Distribution(
                    kind="rouge",
                    col_in_embs=["document_text"],
                    col_in_groupby=["question_idx", "experiment_id"],
                    col_out=["rogue_f1"],
                )
            ],
            plot=[
                PlotlyChart.Histogram(
                    title="Text Overlap between document embeddings",
                    props=dict(x="rogue_f1", nbins=20),
                )
            ],
        )
    )

    checks.append(
        Check(
            name="quality_scores",
            sequence=[
                # DocsLinkVersion(
                #     col_in_text="document_link"
                # ),
                # TextLength(
                #     col_in_text="document_text"
                # ),
                RougeScore(
                    score_type="f1",
                    col_in_generated="response",
                    col_in_source="document_text",
                ),
                Embedding(
                    model="MiniLM-L6-v2",
                    col_in_text="document_text"
                ),
                Embedding(
                    model="MiniLM-L6-v2",
                    col_in_text="response"
                ),                
                Embedding(
                    model="MiniLM-L6-v2",
                    col_in_text="question"
                ),                
                CosineSimilarity(
                    col_in_vector_1="question_embeddings",
                    col_in_vector_2="response_embeddings",
                ),
                # TextComparison(
                #     reference_text="<EMPTY MESSAGE>",
                #     col_in_text="response",
                # ),
            ],
            plot=[
                PlotlyChart.Table(title="Quality scores"),
                PlotlyChart.Bar(
                    title="Bar Plot of Link version",
                    props=dict(x="document_link_version"),
                ),
                PlotlyChart.Histogram(
                    title="Histogram of Context Length",
                    props=dict(x="document_context_length", nbins=20),
                ),
            ],
        )
    )

    checks.append(
        Check(
            name="question_umap",
            sequence=[
                Embedding(
                    model="MiniLM-L6-v2",
                    col_in_text="response",
                    col_out = "response_embeddings"
                ),                
                Embedding(
                    model="MiniLM-L12-v2",
                    col_in_text="question",
                ),                
                UMAP(
                    col_in_embs_1="question_embeddings",
                    col_in_embs_2="response_embeddings",
                )
            ],
            plot=[
                PlotlyChart.Scatter(
                    title="UMAP for question embeddings",
                    props=dict(
                        x="umap_0", y="umap_1", symbol="symbol", color="cluster"
                    ),
                )
            ],
        )
    )

    return CheckSet(
        source=JsonReader(fpath=source_path),
        checks=checks,
        settings=Settings(logs_folder="uptrain_logs"),
    )

cfg = get_checkset(dataset)
cfg.setup()
cfg.run()





# source = [a, b, c, d, e, f]

# @lru_cache
# def embs_1():
#     return ...

# @lru_cache
# def embs_2():
#     return ...


# def cosine(df):
#     embs_1 = embs_1(df)
#     embs_2 = embs_1(embs_1)












# TABLE = [Columns]

# Lineage(Columns) - 
#     3 is added -> 


# check_1 = Check(
#     name = "Cosine sim",
#     compute = [
#         Embeddings(col_in = "a", col_out = "3"),  -> RowCalculation,  
#                     Dependency -> a U Dataset Name U Embedding_model
#         Embeddings(col_in = "3", col_out = "4"),  -> RowCalculation,  Dependency -> b U (a U (a, b, c, d, e, f))
#                     Dependency -> 3 U Dataset Name U Embedding_model
#                     Dependency -> a U Dataset Name U Embedding_model1 U Dataset Name U Embedding_model2
#         CosineSimilarity(col_in = ["3", "4"], col_out = "5")  -> RowCalculation -> a U (a, b, c, d, e, f)
#         Embeddings(col_in = "c", col_out = "8"),  -> RowCalculation,  Dependency -> b U (a U (a, b, c, d, e, f))
#     ],
#     plot = [table, histogram]
# )


# Check -> Takes input data, computes everything and do ploting

# check_4 = Check(
#     name = "Cosine sim",
#     compute = [
#         Embeddings(col_in = "c", col_out = "8"), 
#         CohereEmbeddings(col_in = "a", col_out = "3"),  -> RowCalculation,  
#                     Dependency -> a U Dataset Name U Cohere
#         Embeddings(col_in = "3", col_out = "4"),  -> RowCalculation,  Dependency -> b U (a U (a, b, c, d, e, f))
#                     Dependency -> 3 U Dataset Name U Embedding_model
#                     Dependency -> a U Dataset Name U Embedding_model1 U Dataset Name U Embedding_model2
#         CosineSimilarity(col_in = ["3", "4"], col_out = "5")  -> RowCalculation -> a U (a, b, c, d, e, f)
#         Embeddings(col_in = "c", col_out = "8"),  -> RowCalculation,  Dependency -> b U (a U (a, b, c, d, e, f))
#     ],
#     plot = [table, histogram]
# )


# check_2 = Check(
#     name = "UMAP",
#     compute = [
#         Embeddings(col_in = "a", col_out = "6"), -> RowCalculation, Dependency -> a U (a, b, c, d, e, f) U Dataset Name U Calculation_context
#         UMAP(col_in = "6") -> RowCalculation
#     ],
#     plot = [umap]
# )

# check_3 = Check(
#     name = "Distribution",
#     compute = [
#         Embeddings(col_in = "c", col_out = "9"), -> RowCalculation
#         Distribution(col_in = "7", agg_col = "c", type = "rogue") -> NotRowCalculation
#     ],
#     plot = [umap]
# )