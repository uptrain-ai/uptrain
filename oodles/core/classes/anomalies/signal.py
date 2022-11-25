from oodles.constants import MODEL_SIGNAL_TO_FN_MAPPING


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

    def base_evaluate(self, inputs, outputs, gts=None, extra_args={}):
        extra_args.update(self.extra_args)
        if self.fn is None:
            raise Exception("Evalution fn not defined for signal: ", self.name)
        return self.fn(inputs, outputs, gts=gts, extra_args=extra_args)

    def evaluate(self, inputs, outputs, gts=None, extra_args={}):
        res = self.base_evaluate(inputs, outputs, gts=gts, extra_args=extra_args)
        if not isinstance(res, (int, bool)):
            raise Exception(
                "Unsupported return type: %s for signal: %s"
                % (str(type(res)), self.name)
            )
        if res > 1:
            return True
        if res < 0:
            return False
        return res

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

    def __invert__(self):
        return InvertSignal(self)

    def __str__(self):
        txt = self.name
        if len(self.children):
            txt += "("
            txt += ",".join([str(x) for x in self.children])
            txt += ")"
        return txt


class OperatorSignal(Signal):
    name = ""

    def __init__(self, base, other):
        super().__init__(self.name)
        self.base = base
        self.other = other
        self.children = [base, other]


class AddSignal(OperatorSignal):
    name = "Sum"

    def base_evaluate(self, inputs, outputs, gts=None, extra_args={}):
        return self.base.evaluate(
            inputs, outputs, gts=gts, extra_args=extra_args
        ) + self.other.evaluate(inputs, outputs, gts=gts, extra_args=extra_args)


class MulSignal(OperatorSignal):
    name = "Product"

    def base_evaluate(self, inputs, outputs, gts=None, extra_args={}):
        return self.base.evaluate(
            inputs, outputs, gts=gts, extra_args=extra_args
        ) * self.other.evaluate(inputs, outputs, gts=gts, extra_args=extra_args)


class AndSignal(OperatorSignal):
    name = "And"

    def base_evaluate(self, inputs, outputs, gts=None, extra_args={}):
        return self.base.evaluate(
            inputs, outputs, gts=gts, extra_args=extra_args
        ) & self.other.evaluate(inputs, outputs, gts=gts, extra_args=extra_args)


class OrSignal(OperatorSignal):
    name = "Or"

    def base_evaluate(self, inputs, outputs, gts=None, extra_args={}):
        return self.base.evaluate(
            inputs, outputs, gts=gts, extra_args=extra_args
        ) | self.other.evaluate(inputs, outputs, gts=gts, extra_args=extra_args)


class XorSignal(OperatorSignal):
    name = "Xor"

    def base_evaluate(self, inputs, outputs, gts=None, extra_args={}):
        return self.base.base_evaluate(
            inputs, outputs, gts=gts, extra_args=extra_args
        ) ^ self.other.evaluate(inputs, outputs, gts=gts, extra_args=extra_args)


class InvertSignal(Signal):
    def __init__(self, base):
        super().__init__("Invert")
        self.base = base
        self.children = [base]

    def base_evaluate(self, inputs, outputs, gts=None, extra_args={}):
        return ~self.base.base_evaluate(inputs, outputs, gts=gts, extra_args=extra_args)
