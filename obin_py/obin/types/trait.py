from obin.types.root import W_Hashable
from obin.types import api, space, plist
from obin.misc import platform


def find_by_name(name, method):
    return api.equal_b(method.name, name)


class W_Trait(W_Hashable):
    # _immutable_fields_ = ['_name_']

    def __init__(self, name, constraints):
        W_Hashable.__init__(self)
        self.name = name
        self.methods = plist.empty()
        self.constraints = constraints

    def _at_(self, key):
        return plist.find_with(self.methods, key, find_by_name)

    def add_method(self, method):
        assert space.isgeneric(method)
        self.methods = plist.cons(method, self.methods)

    def has_method(self, method):
        return plist.contains(self.methods, method)

    def _type_(self, process):
        return process.std.types.Trait

    def _compute_hash_(self):
        return int((1 - platform.random()) * 10000000)

    def _to_string_(self):
        return api.to_s(self.name)
        # return "<trait %s>" % (api.to_s(self.name))

    def _to_repr_(self):
        return self._to_string_()

    def _equal_(self, other):
        return other is self
