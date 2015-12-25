from obin.runtime.reference import Reference
from obin.objects import api
from obin.objects.space import isstring
from obin.utils.builtins import is_absent_index


def newenv(obj, outer_environment):
    env = Environment(obj, outer_environment)
    return env


def get_reference(lex, identifier):
    # print "get_reference lex", lex
    if lex is None:
        return None

    index = lex.get_index(identifier)
    if not is_absent_index(index):
        ref = Reference(lex, identifier, index)
        return ref
    else:
        outer = lex.outer_environment
        return get_reference(outer, identifier)


class Environment:
    _immutable_fields_ = ['binding_object', 'outer_environment']

    def __init__(self, obj, outer_environment=None):
        assert isinstance(outer_environment, Environment) or outer_environment is None
        self.outer_environment = outer_environment
        self.binding = obj

    def get_reference(self, identifier):
        # print "Environment.get_reference"
        return get_reference(self.outer_environment, identifier)

    def set_local(self, idx, v):
        api.put_at_index(self.binding, idx, v)

    def get_index(self, n):
        return api.get_index(self.binding, n)

    def get_local(self, idx):
        return api.at_index(self.binding, idx)

    def has_binding(self, n):
        assert isstring(n)
        return api.n_contains(self.binding, n)

    def set_binding(self, n, v):
        assert isstring(n)
        api.put(self.binding, n, v)

    def get_binding_value(self, n):
        assert isstring(n)
        return api.at(self.binding, n)
