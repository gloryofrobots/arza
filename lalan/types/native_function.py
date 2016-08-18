from lalan.types.root import W_Callable
from lalan.runtime import error
from lalan.types import api, space, partial
from lalan.misc.platform import jit


class W_NativeFunction(W_Callable):
    # _immutable_fields_ = ['_name_', 'arity',  '_function_']

    def __init__(self, name, function, arity):
        self._name_ = name
        self._function_ = function
        self.arity = arity

    def _to_string_(self):
        return "fun %s/%d [native code]" % (api.to_s(self._name_), self.arity)

    def _to_repr_(self):
        return self._to_string_()

    def _type_(self, process):
        return process.std.types.Function

    def _to_routine_(self, stack, args):
        from lalan.runtime.routine.routine import create_native_routine
        if self.arity != -1 and api.length_i(args) != self.arity:
            return error.throw_3(error.Errors.INVOKE_ERROR,
                                 space.newstring(u"Invalid native call wrong count of arguments"),
                                 args, self)

        routine = create_native_routine(stack, self._name_, self._function_, args, self.arity)

        routine = jit.promote(routine)
        return routine

    def _call_(self, process, args):
        process.call_object(self, args)

    def _equal_(self, other):
        from lalan.types import space
        if not space.isnativefunction(other):
            return False

        return self._function_ == other._function_
