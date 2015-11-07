from obin.runtime.reference import Reference
from obin.objects import api
from obin.objects.object_space import isstring


def newenv(outer_environment, size):
    from obin.objects.object_space import newsimpleobject_withsize
    obj = newsimpleobject_withsize(size)
    env = Environment(obj, outer_environment)
    return env


def newobjectenv(obj, outer_environment):
    env = Environment(obj, outer_environment)
    return env


def get_reference(lex, identifier):
    if lex is None:
        return Reference(referenced=identifier)

    exists = lex.has_binding(identifier)
    if exists:
        ref = Reference(base_env=lex, referenced=identifier)
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
        return get_reference(self, identifier)

    def has_binding(self, n):
        assert isstring(n)
        return self.binding.has(n)

    def set_binding(self, n, v):
        assert isstring(n)
        api.put(self.binding, n, v)

    def get_binding_value(self, n):
        assert isstring(n)
        return api.at(self.binding, n)
