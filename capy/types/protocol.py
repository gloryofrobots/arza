from capy.types.root import W_Hashable
from capy.misc import platform
from capy.runtime import error
from capy.types import api, space, plist, array
from capy.compile.parse import nodes


class W_Method(W_Hashable):
    # _immutable_fields_ = ["_name_"]

    def __init__(self, name, arity, arg_indexes, default):
        W_Hashable.__init__(self)
        self.name = name
        self.dispatch_indexes = arg_indexes
        self.arity = arity
        arg_length = len(self.dispatch_indexes)

        if arg_length == 1:
            self.double = False
        elif arg_length == 2:
            self.double = True
        else:
            raise

        self.default = default
        self.dag = None
        self.methods = space.newemptytable()

    def _to_string_(self):
        return "<method %s/%s>" % (api.to_s(self.name), api.to_s(self.arity))

    def _to_repr_(self):
        return self._to_string_()

    def register_double(self, process, type_1, type_2, fn):
        lookup = api.lookup(self.methods, type_1, space.newvoid())
        if space.isvoid(lookup):
            lookup = space.newemptytable()
            api.put(self.methods, type_1, lookup)
        api.put(lookup, type_2, fn)

    def register(self, process, types, fn):
        if self.double:
            return self.register_double(process, types[0], types[1], fn)
        assert api.length_i(types) == 1
        t = types[0]
        api.put(self.methods, t, fn)

    def _dispatch_double(self, process, args):
        index = self.dispatch_indexes[0]
        _arg = api.at_index(args, index)
        _type = api.get_type(process, _arg)
        table = api.lookup(self.methods, _type, space.newvoid())

        if space.isvoid(table):
            return error.throw_3(error.Errors.METHOD_NOT_IMPLEMENTED_ERROR,
                                 self,
                                 array.types_array(process, args),
                                 args)

        self.__dispatch_single(process, args, self.dispatch_indexes[1], table)
        # dispatch_args = space.newtuple([args[i] for i in self.dispatch_indexes])
        # print "####", str(self.name)
        # print "####", args
        # print "----", method
        # method = lookup_implementation(process, self, args)
        pass

    def __dispatch_single(self, process, args, index, methods):
        _arg = api.at_index(args, index)
        _type = api.get_type(process, _arg)
        method = api.lookup(methods, _type, space.newvoid())
        if space.isvoid(method):
            return error.throw_3(error.Errors.METHOD_NOT_IMPLEMENTED_ERROR,
                                 self,
                                 array.types_array(process, args),
                                 args)

        assert method is not self
        api.call(process, method, args)

    def _dispatch_single(self, process, args):
        return self.__dispatch_single(process, args, self.dispatch_indexes[0], self.methods)

    def _call_(self, process, args):
        arity = api.length_i(args)
        if arity != self.arity:
            return error.throw_5(error.Errors.INVALID_ARG_COUNT_ERROR,
                                 space.newstring(u"Invalid count of arguments "),
                                 self, args, space.newint(arity), space.newint(self.arity))
        if self.double:
            return self._dispatch_double(process, args)
        else:
            return self._dispatch_single(process, args)

    def _type_(self, process):
        return process.std.classes.Function

    def _equal_(self, other):
        return self is other

    def _compute_hash_(self):
        return int((1 - platform.random()) * 10000000)


def newmethod(process, func, dispatch_indexes):
    if space.isint(dispatch_indexes):
        int_indexes = [api.to_i(dispatch_indexes)]
    else:
        int_indexes = [api.to_i(index) for index in dispatch_indexes]

    return W_Method(func.name, func.arity, int_indexes, func)
