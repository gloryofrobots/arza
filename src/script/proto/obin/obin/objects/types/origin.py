from obin.objects.types.root import W_Callable
from obin.objects import api
from rpython.rlib import jit


class W_Origin(W_Callable):
    # _immutable_fields_ = ['_name_', 'arity',  '_function_']

    def __init__(self, function):
        from obin.objects.space import newtrait
        self.name = function.name
        self.constructor = function
        self.trait = newtrait(self.name)

    def _tostring_(self):
        return "<origin %s>" % api.to_native_string(self.trait)

    def _behavior_(self, process):
        return process.std.behaviors.Origin

    def _call_(self, process, args):
        process.call_object(self, args)

    def _to_routine_(self, stack, args):
        from obin.runtime.routine import create_origin_routine

        routine = create_origin_routine(stack, self.constructor, args)

        routine = jit.promote(routine)
        return routine


