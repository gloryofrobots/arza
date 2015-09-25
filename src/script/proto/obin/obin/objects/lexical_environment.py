#from rpython.rlib import jit
from obin.runtime.reference import Reference


def get_identifier_reference(lex, identifier):
    assert isinstance(identifier, unicode)
    if lex is None:
        return Reference(referenced=identifier)

    envRec = lex.environment_record
    exists = envRec.has_binding(identifier)
    if exists:
        ref = Reference(base_env=envRec, referenced=identifier)
        return ref
    else:
        outer = lex.outer_environment
        return get_identifier_reference(outer, identifier)


class LexicalEnvironment(object):
    _immutable_fields_ = ['outer_environment', 'environment_record']

    def __init__(self, outer_environment=None):
        assert isinstance(outer_environment, LexicalEnvironment) or outer_environment is None
        self.outer_environment = outer_environment
        self.environment_record = None

    def get_identifier_reference(self, identifier):
        return get_identifier_reference(self, identifier)


class DeclarativeEnvironment(LexicalEnvironment):
    def __init__(self, outer_environment=None, env_size=0, env_resize=True):
        LexicalEnvironment.__init__(self, outer_environment)
        from obin.runtime.environment_record import DeclarativeEnvironmentRecord
        self.environment_record = DeclarativeEnvironmentRecord(env_size, env_resize)


class ObjectEnvironment(LexicalEnvironment):
    def __init__(self, obj, outer_environment=None):
        LexicalEnvironment.__init__(self, outer_environment)
        from obin.runtime.environment_record import ObjectEnvironmentRecord
        self.environment_record = ObjectEnvironmentRecord(obj)
