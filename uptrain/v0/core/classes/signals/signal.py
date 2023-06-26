import numpy as np
import json_fix

from uptrain.v0.constants import MODEL_SIGNAL_TO_FN_MAPPING


class Signal:
    """
    Signal Class to identify edge cases

    ...
    Attributes
    ----------
    name : str
        User-friendly name of the signal
    fn : func
        Signal evaluation func. If evaluated as true, data-point is considered as interesting.
    is_model_signal: bool
        Model signals are defined as part of the framework. Hence, users don't need to define evaluation funcs for them.
    extra_args: dict
        Any signal-specific args (ex: THRESHOLD)

    Methods
    -------
    evaluate(inputs, outputs, extra_args={}):
        Evaluates on given inputs, outputs and return a bool
    """

    def __init__(self, name, fn=None, is_model_signal=False, extra_args={}):
        self.name = name
        if is_model_signal and (fn is None):
            if not name in MODEL_SIGNAL_TO_FN_MAPPING:
                raise Exception(
                    "Evalution fn for signal: %s is not defined in constants" % name
                )
            fn = MODEL_SIGNAL_TO_FN_MAPPING[name]
        self.fn = fn
        self.extra_args = extra_args
        self.children = []

    def __json__(self):
        return {"feature_name": str(self)}

    def base_evaluate(self, inputs, outputs, gts=None, extra_args={}):
        extra_args.update(self.extra_args)
        if self.fn is None:
            raise Exception("Evalution fn not defined for signal: ", self.name)
        return self.fn(inputs, outputs, gts=gts, extra_args=extra_args)

    def evaluate(self, inputs, outputs, gts=None, extra_args={}):
        res = self.base_evaluate(inputs, outputs, gts=gts, extra_args=extra_args)
        return np.array(res)

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
        txt = str(self.name)
        if len(self.children):
            txt += "("
            txt += ",".join([str(x) for x in self.children])
            txt += ")"
        return txt


class InvertSignal(Signal):
    def __init__(self, base):
        super().__init__("Invert")
        self.base = base
        self.children = [base]

    def base_evaluate(self, inputs, outputs, gts=None, extra_args={}):
        base_res = self.base.evaluate(inputs, outputs, gts=gts, extra_args=extra_args)
        return np.logical_not(base_res)


class OperatorSignal(Signal):
    name = ""

    def __init__(self, base, other):
        super().__init__(self.name)
        self.base = base
        self.other = other
        self.children = [base, other]

    def base_evaluate(self, inputs, outputs, gts=None, extra_args={}):
        base_res = self.base.evaluate(inputs, outputs, gts=gts, extra_args=extra_args)
        if isinstance(self.other, Signal):
            other_res = self.other.evaluate(
                inputs, outputs, gts=gts, extra_args=extra_args
            )
        else:
            other_res = [self.other] * len(base_res)
        return self.operator(base_res, other_res)


class AddSignal(OperatorSignal):
    name = "Sum"

    def operator(self, base_res, other_res):
        return base_res + other_res


class MulSignal(OperatorSignal):
    name = "Product"

    def operator(self, base_res, other_res):
        return base_res * other_res


class AndSignal(OperatorSignal):
    name = "And"

    def operator(self, base_res, other_res):
        return np.logical_and(base_res, other_res)


class OrSignal(OperatorSignal):
    name = "Or"

    def operator(self, base_res, other_res):
        return np.logical_or(base_res, other_res)


class XorSignal(OperatorSignal):
    name = "Xor"

    def operator(self, base_res, other_res):
        return np.logical_xor(base_res, other_res)


class GreaterThanSignal(OperatorSignal):
    name = "Greater Than"

    def operator(self, base_res, other_res):
        return np.greater(base_res, other_res)


class LessThanSignal(OperatorSignal):
    name = "Less Than"

    def operator(self, base_res, other_res):
        return np.less(base_res, other_res)


class EqualToSignal(OperatorSignal):
    name = "Equal"

    def operator(self, base_res, other_res):
        return np.equal(base_res, other_res)


class GreaterEqualToSignal(OperatorSignal):
    name = "Greater Equal To"

    def operator(self, base_res, other_res):
        return np.greater_equal(base_res, other_res)


class LessEqualToSignal(OperatorSignal):
    name = "Less Equal To"

    def operator(self, base_res, other_res):
        return np.less_equal(base_res, other_res)


class NotEqualToSignal(OperatorSignal):
    name = "Not Equal"

    def operator(self, base_res, other_res):
        return np.not_equal(base_res, other_res)
