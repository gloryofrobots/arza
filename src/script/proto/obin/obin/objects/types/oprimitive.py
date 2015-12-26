from oroot import W_Callable
from obin.runtime.exception import *
from obin.objects import api
from rpython.rlib import jit


class W_Primitive(W_Callable):
    # _immutable_fields_ = ['_name_', 'arity',  '_function_']

    def __init__(self, name, function, arity):
        self._name_ = name
        self._function_ = function
        self.arity = arity

    def _tostring_(self):
        return "function %s {[native code]}" % api.to_native_string(self._name_)

    def _tobool_(self):
        return True

    def _traits_(self):
        from obin.objects.space import stdlib
        return stdlib.traits.PrimitiveTraits

    def _to_routine_(self, args):
        from obin.runtime.routine import create_primitive_routine

        routine = create_primitive_routine(self._name_, self._function_, args, self.arity)

        routine = jit.promote(routine)
        return routine

    def _call_(self, process, args):
        if self.arity != -1 and api.n_length(args) != self.arity:
            raise ObinRuntimeError(u"Invalid primitive call wrong count of arguments %d != %d"
                                   % (api.n_length(args), self.arity))

        process.call_object(self, args)
