from lalan.types.root import W_Hashable
from lalan.types import api, space, plist
from lalan.misc import platform
from lalan.runtime import error


def find_by_name(name, record):
    generic = api.at_index(record, 1)
    return api.equal_b(generic.name, name)


def contains_generic(method, record):
    generic = api.at_index(record, 1)
    return api.equal_b(generic, method)


class W_Interface(W_Hashable):
    # _immutable_fields_ = ['_name_']

    def __init__(self, name, generics):
        W_Hashable.__init__(self)
        self.name = name
        self.generics = generics
        for record in generics:
            generic = api.at_index(record, 0)
            position = api.at_index(record, 1)
            generic.register_interface(self, position)

    # def find_generic_by_name(self, name):
    #     return plist.find_with(self.generics, name, find_by_name)
    #
    # def has_generic_name(self, name):
    #     return not space.isvoid(plist.find_with(self.generics, name, find_by_name))
    #
    # def has_generic(self, method):
    #     return plist.contains_with(self.generics, method, contains_generic)

    def _at_(self, key):
        return plist.find_with(self.generics, key, find_by_name)

    def _type_(self, process):
        return process.std.types.Interface

    def _compute_hash_(self):
        return int((1 - platform.random()) * 10000000)

    def _to_string_(self):
        return api.to_s(self.name)
        # return "<trait %s>" % (api.to_s(self.name))

    def _to_repr_(self):
        return self._to_string_()

    def _equal_(self, other):
        return other is self


def interface(name, generics):
    result = []
    for record in generics:
        if space.istuple(record):
            error.affirm_type(api.at_index(record, 0), space.isgeneric)
            error.affirm_type(api.at_index(record, 1), space.isint)
            result.append(record)
        else:
            generic = record
            error.affirm_type(generic, space.isgeneric)
            if len(generic.dispatch_indexes) != 1:
                error.throw_2(error.Errors.TYPE_ERROR,
                              space.newstring(u"Impossible to determine argument position for generic function"
                                              u"Specify argument position for function"), generic)

            position = space.newint(generic.dispatch_indexes[0])
            result.append(space.newtuple([generic, position]))

    return W_Interface(name, result)
