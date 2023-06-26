from uptrain.framework.checks import SimpleCheck
from uptrain.operators.language import (
    Embedding,
    RougeScore,
    DocsLinkVersion,
    TextLength,
    TextComparison,
    ModelGradeScore,
    OpenAIGradeScore
)
from uptrain.operators.language.sql import HasStar, ParseSQL, ValidateTables, ExecuteSQL, GetSchemaDefinition

from uptrain.operators import (
    PlotlyChart,
    Distribution,
    CosineSimilarity,
    UMAP
)

prompt_template = """
    You are a {persona} whose job is to only output SQL command for a given question in {dialect} SQL dialect. Do not output anything other than the SQL command.
    
    Here is the create table commands for my database:
    {schema_def}
    
    {question}
    
    SQL:
"""

select_all_check = SimpleCheck(
        name="Query has star symbol",
        compute=[
            HasStar(
                col_in_text="response",
                col_out="has_star_symbol_in_query"
            ),
        ],
        plot=PlotlyChart.Histogram(
            title="Distribution: Generated SQL query has '*' symbol",
            props=dict(x="has_star_symbol_in_query", nbins=2, color='model', barmode='group'),
        ),
    )


# sql_validity_check = SimpleCheck(
#             name="Validate SQL",
#             compute=[
#                 ParseSQL(
#                     col_in_sql="response",
#                     col_out_tables="response_tables",
#                     col_out_is_valid_sql="is_sql_valid"
#                 )
#             ],
#             plot=PlotlyChart(
#                 kind="table",
#                 title="SQL Validity Score",
#             ),
#         )

sql_validity_check = SimpleCheck(
            name="Validate SQL",
            compute=[
                ParseSQL(
                    col_in_sql="response",
                    col_out_tables="response_tables",
                    col_out_is_valid_sql="is_sql_valid"
                ),
                ValidateTables(col_in_response_tables="response_tables",
                               col_in_schema_tables="schema_tables",
                               col_out_tables_valid="tables_valid",
                               col_out_cols_valid="cols_valid")
            ],
        plot=PlotlyChart.Histogram(
            title="Distribution: Generated SQL query is valid",
            props=dict(x="cols_valid", nbins=2, color='model', barmode='group'),
        ),
    )

execution_accuracy_check = SimpleCheck(
            name="Generated SQL query execution accuracy",
            compute=[
                ExecuteSQL(col_in_response_sql="response",
                           col_in_gt_sql="gt_query",
                           col_in_db_path="db_path",
                           col_out_execution_accuracy="execution_accuracy")
            ],
        plot=PlotlyChart.Histogram(
            title="Distribution: SQL execution gives correct results",
            props=dict(x="execution_accuracy", nbins=2, color='model', barmode='group'),
        ),
        )