from obin.types.root import W_Hashable
from obin.runtime import error
from obin.types import api, space
from obin.misc import platform
from obin.builtins.hotpath import HotPath


class W_Generic(W_Hashable):
    # _immutable_fields_ = ["_name_"]

    def __init__(self, name, arity, dispatch_arg_index, signature, hotpath):
        W_Hashable.__init__(self)

        self.name = name
        self.arity = arity
        self.dispatch_arg_index = dispatch_arg_index

        self.arity = api.length_i(signature)

        self.signature = signature
        self.hot_path = hotpath

    def set_hotpath(self, hotpath):
        self.hot_path = HotPath(hotpath, self.arity)

    def _to_string_(self):
        return "<generic %s %s>" % (api.to_s(self.name), api.to_s(self.signature))

    def _to_repr_(self):
        return self._to_string_()

    def _call_(self, process, args):
        arity = api.length_i(args)
        if arity != self.arity:
            return error.throw_3(error.Errors.INVALID_ARG_COUNT_ERROR, space.newstring(u"Invalid count of arguments "),
                                 space.newint(arity), space.newint(self.arity))

        if self.hot_path is not None:
            res = self.hot_path.apply(process, args)
            if res is not None:
                return res

        method = lookup_implementation(process, self, args)
        if space.isvoid(method):
            return error.throw_2(error.Errors.METHOD_NOT_IMPLEMENTED_ERROR, self, args)

        # print "METHOD CALL", method, args
        process.call_object(method, args)

    def _type_(self, process):
        return process.std.types.Generic

    def _equal_(self, other):
        return self is other

    def _compute_hash_(self):
        return int((1 - platform.random()) * 10000000)


def lookup_implementation(process, generic, args):
    dispatch_arg = api.at_index(args, generic.dispatch_arg_index)
    # print "DISPATCH", method, dispatch_arg, space.isunion(dispatch_arg)
    impl = api.dispatch(process, dispatch_arg, generic)
    return impl


def generic_with_hotpath(name, signature, hotpath):
    arity = api.length_i(signature)
    if arity == 0:
        error.throw_1(error.Errors.METHOD_SPECIALIZE_ERROR, space.newstring(u"Generic arity == 0"))
    if arity == 1:
        index = 1
    else:
        index = -1
        for i, sym in enumerate(signature):
            if api.to_s(sym).startswith("`"):
                # instead of break check for multiple ticks
                if index != -1:
                    return error.throw_1(error.Errors.METHOD_SPECIALIZE_ERROR,
                                         space.newstring(u"Generic support only single dispatch signatures"))

                index = i + 1

        if index == -1:
            return error.throw_1(error.Errors.METHOD_SPECIALIZE_ERROR,
                                 space.newstring(u"Generic type variable not determined"))

    h = HotPath(hotpath, arity) if hotpath is not None else None
    return W_Generic(name, arity, index, signature, h)


def generic(name, signature):
    return generic_with_hotpath(name, signature, None)
