import numpy as np
import polars as pl

class Signal:
    """
    Signal Class wrapper for any dataframe column

    Attributes:
        col_name (str): Column Name
        identifier (str): Used as an identifier for printing 

    Methods:
        run(self, data): Evaluates on given data
        
    """

    def __init__(self, col_name=""):
        self.col_name = col_name
        self.identifier = self.col_name
        self.children = []

    def __json__(self):
        return {"col_name": str(self)}

    def run(self, data: pl.DataFrame) -> pl.Series:
        return data[self.col_name].to_numpy()

    def __invert__(self):
        return InvertSignal(self)

    def __add__(self, other):
        return AddSignal(self, other)

    def __mul__(self, other):
        return MulSignal(self, other)

    def __and__(self, other):
        return AndSignal(self, other)

    def __or__(self, other):
        return OrSignal(self, other)

    def __xor__(self, other):
        return XorSignal(self, other)

    def __gt__(self, other):
        return GreaterThanSignal(self, other)

    def __lt__(self, other):
        return LessThanSignal(self, other)

    def __eq__(self, other):
        return EqualToSignal(self, other)

    def __ge__(self, other):
        return GreaterEqualToSignal(self, other)

    def __le__(self, other):
        return LessEqualToSignal(self, other)

    def __ne__(self, other):
        return NotEqualToSignal(self, other)

    def __str__(self):
        txt = str(self.identifier)
        if len(self.children):
            txt += "("
            txt += ",".join([str(x) for x in self.children])
            txt += ")"
        return txt


class InvertSignal(Signal):
    def __init__(self, base):
        self.identifier = "Invert"
        self.base = base
        self.children = [base]

    def run(self, data: pl.DataFrame) -> pl.Series:
        base_res = self.base.run(data)
        return np.logical_not(base_res)


class OperatorSignal(Signal):

    def __init__(self, base, other):
        self.base = base
        self.other = other
        self.children = [base, other]

    def run(self, data: pl.DataFrame) -> pl.Series:
        base_res = self.base.run(data)
        if isinstance(self.other, Signal):
            other_res = self.other.run(data)
        else:
            other_res = [self.other] * len(base_res)
        return self.operator(base_res, other_res)

    def operator(self, base_res, other_res):
        raise Exception("Should be defined in derived class")


class AddSignal(OperatorSignal):
    identifier = "Sum"

    def operator(self, base_res, other_res):
        return base_res + other_res


class MulSignal(OperatorSignal):
    identifier = "Product"

    def operator(self, base_res, other_res):
        return base_res * other_res


class AndSignal(OperatorSignal):
    identifier = "And"

    def operator(self, base_res, other_res):
        return np.logical_and(base_res, other_res)


class OrSignal(OperatorSignal):
    identifier = "Or"

    def operator(self, base_res, other_res):
        return np.logical_or(base_res, other_res)


class XorSignal(OperatorSignal):
    identifier = "Xor"

    def operator(self, base_res, other_res):
        return np.logical_xor(base_res, other_res)


class GreaterThanSignal(OperatorSignal):
    identifier = "Greater Than"

    def operator(self, base_res, other_res):
        return np.greater(base_res, other_res)


class LessThanSignal(OperatorSignal):
    identifier = "Less Than"

    def operator(self, base_res, other_res):
        return np.less(base_res, other_res)


class EqualToSignal(OperatorSignal):
    identifier = "Equal"

    def operator(self, base_res, other_res):
        return np.equal(base_res, other_res)


class GreaterEqualToSignal(OperatorSignal):
    identifier = "Greater Equal To"

    def operator(self, base_res, other_res):
        return np.greater_equal(base_res, other_res)


class LessEqualToSignal(OperatorSignal):
    identifier = "Less Equal To"

    def operator(self, base_res, other_res):
        return np.less_equal(base_res, other_res)


class NotEqualToSignal(OperatorSignal):
    identifier = "Not Equal"

    def operator(self, base_res, other_res):
        return np.not_equal(base_res, other_res)
