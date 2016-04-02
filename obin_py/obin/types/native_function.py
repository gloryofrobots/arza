from obin.types.root import W_Callable
from obin.runtime import error
from obin.types import api, space, partial
from obin.misc.platform import jit


class W_NativeFunction(W_Callable):
    # _immutable_fields_ = ['_name_', 'arity',  '_function_']

    def __init__(self, name, function, arity):
        self._name_ = name
        self._function_ = function
        self.arity = arity

    def _to_string_(self):
        return "fun %s/%d [native code]" % (api.to_s(self._name_), self.arity)

    def _type_(self, process):
        return process.std.types.NativeFunction

    def _to_routine_(self, stack, args):
        from obin.runtime.routine.routine import create_native_routine
        if self.arity != -1 and api.length_i(args) != self.arity:
            return error.throw_3(error.Errors.INVOKE_ERROR,
                                 space.newstring(u"Invalid native call wrong count of arguments"),
                                 args, self)

        routine = create_native_routine(stack, self._name_, self._function_, args, self.arity)

        routine = jit.promote(routine)
        return routine

    def _call_(self, process, args):
        if self.arity != -1:
            length = api.length_i(args)
            if length < self.arity:
                return partial.newfunction_partial(self, args)

        process.call_object(self, args)

    def _equal_(self, other):
        from obin.types import space
        if not space.isnativefunction(other):
            return False

        return self._function_ == other._function_
