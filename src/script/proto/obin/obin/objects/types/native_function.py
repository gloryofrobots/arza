from obin.objects.types.root import W_Callable
from obin.runtime.error import *
from obin.objects import api
from rpython.rlib import jit


class W_NativeFunction(W_Callable):
    # _immutable_fields_ = ['_name_', 'arity',  '_function_']

    def __init__(self, name, function, arity):
        self._name_ = name
        self._function_ = function
        self.arity = arity

    def _tostring_(self):
        return "function %s {[native code]}" % api.to_native_string(self._name_)

    def _tobool_(self):
        return True

    def _behavior_(self, process):
        return process.std.behaviors.Primitive

    def _to_routine_(self, stack, args):
        from obin.runtime.routine import create_native_routine

        routine = create_native_routine(stack, self._name_, self._function_, args, self.arity)

        routine = jit.promote(routine)
        return routine

    def _call_(self, process, args):
        if self.arity != -1 and api.n_length(args) != self.arity:
            raise ObinRuntimeError(u"Invalid native call wrong count of arguments %d != %d"
                                   % (api.n_length(args), self.arity))

        process.call_object(self, args)

    def _equal_(self, other):
        from obin.objects import space
        if not space.isnativefunction(other):
            return False

        return self._function_ == other._function_
