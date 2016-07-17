from obin.types.root import W_Hashable
from obin.types import api, space, plist
from obin.misc import platform
from obin.runtime import error


class W_Trait(W_Hashable):
    # _immutable_fields_ = ['_name_']

    def __init__(self, name, constraints):
        W_Hashable.__init__(self)
        self.name = name
        self.constraints = constraints

        self.methods = space.newmap()

    def _at_(self, generic):
        assert space.isgeneric(generic), generic
        return api.at(self.methods, generic)

    def to_list(self):
        return self.methods.to_list()
    
    def add_method(self, generic, method):
        assert space.isgeneric(generic)
        assert space.isfunction(generic)

        api.put(self.methods, generic, method)

    def has_method(self, generic):
        return api.contains(self.methods, generic)

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


def trait(name, constraints, methods):
    _t = W_Trait(name, constraints)

    error.affirm_type(methods, space.islist)
    for data in methods:
        error.affirm_type(data, space.istuple)
        generic = data[0]
        impl = data[1]
        _t.add_method(generic, impl)

    return _t
