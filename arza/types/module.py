from arza.types import api, space, plist, symbol
from arza.types.root import W_Root, W_Callable
from arza.misc.platform import is_absent_index
from arza.runtime import error


class W_Module(W_Root):
    _immutable_fields_ = ['name', 'data']

    def __init__(self, name, data, env):
        self.name = name
        self.data = data
        self.env = env

    def can_export(self, symbol):
        return api.contains_b(self.data, symbol)

    def exports(self):
        return self.data.keys_list()

    def _type_(self, process):
        return process.std.types.Module

    def has(self, n):
        return self.data._contains_(n)

    def get(self, n):
        return self.data._at_(n)

    def _at_(self, n):
        assert space.issymbol(n)
        return self.env._at_(n)

    def _contains_(self, key):
        return self.env._contains_(key)

    def _equal_(self, other):
        if not isinstance(other, W_Module):
            return False
        # print "EQ", self, other
        return api.equal_b(self.name, other.name) and api.equal_b(self.data, other.data)

    def _to_string_(self):
        return "<Module %s %r>" % (self.name, self.data.keys())

    def _to_repr_(self):
        return self._to_string_()


def newmodule(env):
    name = env.name
    values = env.exported_values()
    return W_Module(name, values, env)


