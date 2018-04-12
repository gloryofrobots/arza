from arza.types.root import W_Hashable
from arza.types import api, space, plist
from arza.misc import platform
from arza.runtime import error


def find_by_name(name, record):
    generic = api.at_index(record, 1)
    return api.equal_b(generic.name, name)


def contains_generic(method, record):
    generic = api.at_index(record, 1)
    return api.equal_b(generic, method)


class W_Interface(W_Hashable):
    # _immutable_fields_ = ['_name_']

    def __init__(self, name, generics, sub_interfaces):
        W_Hashable.__init__(self)
        self.name = name
        self.types = plist.empty()

        self.sub_interfaces = sub_interfaces

        # generics already have all values from sub_interfaces
        self.generics = generics

    def count_generics(self):
        count = api.length_i(self.generics)
        return count

    def register_type(self, type):
        if api.contains_b(self.types, type):
            error.throw_3(error.Errors.TYPE_ERROR,
                          space.newstring(u"Type already registered in interface"), self, type)

        self.types = plist.cons(type, self.types)

    def _at_(self, key):
        return plist.find_with(self.generics, key, find_by_name)

    def _type_(self, process):
        return process.std.types.Interface

    def _compute_hash_(self):
        return int((1 - platform.random()) * 10000000)

    def _to_string_(self):
        return "<I: %s>" % (api.to_s(self.name))

    def _to_repr_(self):
        return self._to_string_()

    def _equal_(self, other):
        return other is self


def interface(name, generics, sub_interfaces):
    result = plist.empty()
    for record in generics:
        error.affirm_type(record, space.istuple)
        gf = api.at_index(record, 0)
        index = api.at_index(record, 1)
        error.affirm_type(gf, space.isgeneric)
        error.affirm_type(index, space.isint)

        gf.register_dispatch_index(api.to_i(index))

        result = plist.cons(record, result)

    if not api.is_empty_b(sub_interfaces):
        # print "BEFORE", result
        for iface in sub_interfaces:
            for record in iface.generics:
                if not api.contains_b(result, record):
                    result = plist.cons(record, result)
                    # print "AFTER", result

    return W_Interface(name, result, sub_interfaces)
