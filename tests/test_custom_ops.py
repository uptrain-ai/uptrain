from uptrain.operators import register_custom_op, ColumnOp


@register_custom_op
class Sum(ColumnOp):
    col_a: str
    col_b: str

    def setup(self, settings):
        return self

    def run(self, data):
        import polars as pl

        return {
            "output": data.with_columns(
                [(pl.col(self.col_a) + pl.col(self.col_b)).alias("sum")]
            )
        }


def test_custom_op():
    """Test the custom operator by serializing and deserializing it."""
    import polars as pl
    from uptrain.framework import Check, Settings

    ds = pl.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    op_sum = Sum(col_a="a", col_b="b")
    check = Check(name=op_sum, operators=[op_sum], plots=[])

    out = check.setup(Settings()).run(ds)
    assert out["sum"].series_equal(pl.Series("sum", [5, 7, 9]))

    serialized = check.dict()
    check_2 = Check.from_dict(serialized)
    out_2 = check_2.setup(Settings()).run(ds)
    assert out_2["sum"].series_equal(pl.Series("sum", [5, 7, 9]))
