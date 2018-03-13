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

    def _put_at_index_(self, idx, v):
        return self.data._put_at_index_(idx, v)

    def _get_index_(self, n):
        return self.data._get_index_(n)

    def _at_index_(self, i):
        return self.data._at_index_(i)

    def _put_(self, k, v):
        assert space.issymbol(k)
        return self.data._put_(k, v)

    def _at_(self, n):
        assert space.issymbol(n)
        return self.data._at_(n)

    def _contains_(self, key):
        return self.data._contains_(key)

    def _equal_(self, other):
        if not isinstance(other, W_Module):
            return False
        # print "EQ", self, other
        return api.equal_b(self.name, other.name) and api.equal_b(self.data, other.data)

    def _to_string_(self):
        return "<Module %s %s>" % (self.name, self.data._to_string_())

    def _to_repr_(self):
        return self._to_string_()


def newmodule(env):
    name = env.name
    values = env.exported_values()
    return W_Module(name, values, env)


def submodule(process, module, names):
    data = space.newassocarray()
    for name in names:
        value = api.at(module.data, name)
        api.put(data, name, value)

    subsymbol = space.newsymbol(process, u".sub")
    module_name = symbol.concat_2(process, subsymbol, module.name)
    return W_Module(module_name, data, module.env)
