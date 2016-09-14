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

        self.generics = generics

        # for record in generics:
        #     generic = api.at_index(record, 0)
        #     position = api.at_index(record, 1)
        #     generic.register_interface(self, position)

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
        return "<interface %s>" % (api.to_s(self.name))

    def _to_repr_(self):
        return self._to_string_()

    def _equal_(self, other):
        return other is self


def interface(name, generics, sub_interfaces):
    result = plist.empty()
    for record in generics:
        if space.istuple(record):
            error.affirm_type(api.at_index(record, 0), space.isgeneric)
            error.affirm_type(api.at_index(record, 1), space.isint)
        else:
            # TODO make interface accept all positions in that case
            generic = record
            error.affirm_type(generic, space.isgeneric)
            position = space.newint(generic.dispatch_indexes[0])
            record = space.newtuple([generic, position])

        result = plist.cons(record, result)
        # result.append(record)

    if not api.is_empty_b(sub_interfaces):
        print "BEFORE", result
        for iface in sub_interfaces:
            result = plist.concat(result, iface.generics)
        print "AFTER", result

        result = plist.unique(result)
    return W_Interface(name, result, sub_interfaces)
