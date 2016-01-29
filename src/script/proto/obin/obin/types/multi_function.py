from obin.types.root import W_Callable
from obin.runtime import error
from obin.types import api


class W_MultiFunction(W_Callable):
    """
    function which dispatch calls according to arity
    """
    # _immutable_fields_ = ["_name_"]

    def __init__(self, name, methods):
        self.name = name
        self.methods = []
        _add_methods(self, methods)

    def _length_(self):
        return len(self.methods)

    def _tostring_(self):
        return "multifunction %s {}" % api.to_s(self.name)

    def _tobool_(self):
        return True

    def _call_(self, process, args):
        method = _get_method(process, self, args)
        # print "GEN CALL", str(method)
        process.call_object(method, args)

    def _behavior_(self, process):
        return process.std.behaviors.Function


def _get_method(process, func, args):
    arity = api.n_length(args)
    length = api.n_length(func)
    # print "LOOKUP", gf._name_, args, arity

    if arity >= length:
        return error.throw_2(error.Errors.METHOD_INVOKE, func, args)

    method = func.methods[arity]
    if method is None:
        return error.throw_2(error.Errors.METHOD_INVOKE, func, args)

    return method


def _add_method(func, method):
    arity = method.arity
    length = api.n_length(func)

    if arity >= length:
        func.methods = func.methods + ([None] * ((arity + 1) - length))

    func.methods[arity] = method


def _add_methods(func, methods):
    for method in methods.to_list():
        _add_method(func, method)
