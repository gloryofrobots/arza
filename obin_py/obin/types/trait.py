from obin.types.root import W_Hashable
from obin.types import api, space, plist
from obin.misc import platform


class W_Trait(W_Hashable):
    # _immutable_fields_ = ['_name_']

    def __init__(self, name, typevar, constraints):
        W_Hashable.__init__(self)
        self.name = name
        self.typevar = typevar
        self.methods = plist.empty()
        self.constraints = constraints

    def add_method(self, method):
        assert space.ismethod(method)
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

    def _equal_(self, other):
        return other is self

