from obin.types import api, space
from obin.types.root import W_Root
from obin.runtime import error


class W_LazyVal(W_Root):
    def __init__(self, fn):
        self.fn = fn
        self.value = None

    def _to_string_(self):
        return "<LazyValue(%s)>" % api.to_s(self.fn) if self.value is None else api.to_s(self.value)

    def _to_repr_(self):
        return self._to_string_()

    def _type_(self, process):
        return process.std.types.LazyVal

    def on_eval(self, process, result):
        # print "ON EVAL", result
        if space.islazyval(result):
            self.value = process.subprocess(result, space.newtupleunit())
        else:
            self.value = result
        return self.value

    def is_forced(self):
        return self.value is not None

    def _to_routine_(self, stack, args):
        # print "TO ROUTINE"
        from obin.runtime.routine.routine import create_callback_routine
        routine = create_callback_routine(stack, self.on_eval, self.fn, args)
        return routine

    def _call_(self, process, args):
        if self.is_forced():
            # print "LAZY CACHE", self.value
            return self.value

        # print "LAZY CALL", args
        process.call_object(self, args)

    def _equal_(self, other):
        if not self.is_forced():
            return error.throw_1(error.Errors.VALUE_ERROR,
                                 space.newstring(u"Invalid operation on unevaluated lazy value"))

        if space.islazyval(other):
            if not other.is_forced():
                return error.throw_1(error.Errors.VALUE_ERROR,
                                     space.newstring(u"Invalid operation on unevaluated lazy value"))

            return api.equal_b(self.value, other.value)

        return api.equal_b(self.value, other)


def is_forced(lazy):
    error.affirm_type(lazy, space.islazyval)
    return space.newbool(lazy.is_forced())
