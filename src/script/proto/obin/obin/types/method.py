from obin.types.root import W_Callable
from obin.runtime import error
from obin.types import api
from obin.misc import platform
from obin.builtins.hotpath import HotPath


class W_Method(W_Callable):
    # _immutable_fields_ = ["_name_"]

    def __init__(self, name, trait, arity, dispatch_arg_index, typevar, signature, hotpath):
        self.name = name
        self.trait = trait
        self.trait.add_method(self)

        self.arity = arity
        self.dispatch_arg_index = dispatch_arg_index
        self.typevar = typevar

        self.arity = api.length_i(signature)

        self.signature = signature
        self.hot_path = hotpath

    def _to_string_(self):
        return "<method %s of %s>" % (api.to_s(self.name), api.to_s(self.trait))

    def _call_(self, process, args):
        arity = api.length_i(args)
        if self.arity != arity:
            return error.throw_1(error.Errors.INVALID_ARG_COUNT, args)

        if self.hot_path is not None:
            res = self.hot_path.apply(process, args)
            if res is not None:
                process.fiber.push_into_stack(res)
                return

        method = lookup_implementation(process, self, args)
        # print "GEN CALL", str(method)
        process.call_object(method, args)

    def _type_(self, process):
        return process.std.types.Method

    def _equal_(self, other):
        from obin.types import space
        if not space.ismethod(other):
            return False

        if not api.equal_b(self.trait, other.trait):
            return False

        if not api.equal_b(self.name, other.name):
            return False

        return True

    def _compute_hash_(self):
        return int((1 - platform.random()) * 10000000)


def lookup_implementation(process, method, args):
    dispatch_arg = api.at_index(args, method.dispatch_arg_index)
    _type = api.get_type(process, dispatch_arg)
    impl = _type.get_method_implementation(method)
    return impl


def method_with_hotpath(name, trait, signature, hotpath):
    arity = api.length_i(signature)
    typevar = trait.typevar
    if arity == 0:
        error.throw_1(error.Errors.METHOD_SPECIALIZE, u"Method arity == 0")

    dispatch_arg_index = api.get_index(signature, typevar)
    if platform.is_absent_index(dispatch_arg_index):
        error.throw_2(error.Errors.METHOD_SPECIALIZE,
                      u"Unspecified type variable in method signature. expected variable", typevar)

    return W_Method(name, trait, arity, dispatch_arg_index, typevar, signature, HotPath(hotpath, arity))


def method(name, trait, signature):
    return method_with_hotpath(name, trait, signature, None)
