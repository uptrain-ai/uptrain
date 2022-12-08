def signal_fn(func):
    def inner(inputs, outputs, gts=None, extra_args={}):
        return func(inputs, outputs, gts=gts, extra_args=extra_args)

    return inner


def monitor(framework_obj):
    def decorator(fn):
        def wrapped(model, inputs):
            outputs = fn(model, inputs)
            identifiers = framework_obj.check_and_add_data(inputs, outputs)
            if framework_obj.need_retraining():
                framework_obj.retrain()
            return outputs, identifiers

        return wrapped

    return decorator
