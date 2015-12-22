from obin.runtime.reference import Reference
from obin.objects import api
from obin.objects.space import isstring


def newenv(obj, outer_environment):
    env = Environment(obj, outer_environment)
    return env


def get_reference(lex, identifier):
    if lex is None:
        return None

    index = lex.get_index(identifier)
    if index is not -1000:
        ref = Reference(lex, identifier, index)
        return ref
    else:
        outer = lex.outer_environment
        return get_reference(outer, identifier)


class Environment(object):
    _immutable_fields_ = ['binding_object', 'outer_environment']

    def __init__(self, obj, outer_environment=None):
        super(Environment, self).__init__()
        assert isinstance(outer_environment, Environment) or outer_environment is None
        self.outer_environment = outer_environment
        self.binding = obj

    def get_reference(self, identifier):
        return get_reference(self.outer_environment, identifier)

    def set_local(self, idx, v):
        self.binding.put_by_index(idx, v)

    def get_index(self, n):
        return self.binding.get_index(n)

    def get_local(self, idx):
        return self.binding.get_by_index(idx)

    def has_binding(self, n):
        assert isstring(n)
        return self.binding.has(n)

    def set_binding(self, n, v):
        assert isstring(n)
        api.put(self.binding, n, v)

    def get_binding_value(self, n):
        assert isstring(n)
        return api.at(self.binding, n)
