from obin.objects.types.root import W_Callable
from obin.objects import api


class W_Origin(W_Callable):
    # _immutable_fields_ = ['_name_', 'arity',  '_function_']

    def __init__(self, name, function):
        from obin.objects.space import newtrait
        self.name = name
        self.func = function
        self.trait = newtrait(self.name)

    def _tostring_(self):
        return "<Origin %s>" % api.to_native_string(self.name)

    def _behavior_(self, process):
        return process.std.behaviors.Origin

    def _call_(self, process, args):
        api.call(process, self.func, args)
