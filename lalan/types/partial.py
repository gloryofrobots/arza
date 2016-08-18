from lalan.types.root import W_Callable
from lalan.runtime import error
from lalan.types import api, space, tuples


class W_Partial(W_Callable):
    # _immutable_fields_ = ['scope',  'is_variadic', 'arity', '_name_']

    def __init__(self, func, args):
        self.func = func
        self.args = args
        self.arity = func.arity
        self.count = api.length_i(self.args)

    def _to_string_(self):
        # params = ",".join([api.to_native_string(p) for p in self.bytecode.scope.arguments])
        # return "fn %s(%s){ %s }" % (self._name_.value(), params, self._bytecode_.tostring())
        return "%s with %s" % (api.to_s(self.func), api.to_s(self.args))

    def _to_repr_(self):
        return self._to_string_()

    def _type_(self, process):
        return process.std.types.Partial

    def _call_(self, process, args):
        new_args = tuples.concat(self.args, args)
        length = api.length_i(new_args)
        if length == self.arity:
            # print "CALL", self.func, new_args
            return api.call(process, self.func, new_args)
        elif length < self.arity:
            return W_Partial(self.func, new_args)
        else:
            error.throw_3(error.Errors.INVOKE_ERROR, space.newstring(u"Too mach arguments for partial"),
                          space.newint(length), self.func)

    def _equal_(self, other):
        from lalan.types import space
        if not space.ispartial(other):
            return False

        return api.equal_b(self.func, other.func)


def newpartial(func):
    if space.ispartial(func):
        return func
    error.affirm_type(func, space.isfunction)
    return W_Partial(func, space.newtuple([]))


def newfunction_partial(func, args):
    error.affirm_type(func, space.isfunction)
    error.affirm_type(args, space.istuple)
    error.affirm(api.length_i(args) < func.arity, u"Too many arguments for partial function")
    return W_Partial(func, args)
