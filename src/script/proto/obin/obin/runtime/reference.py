from obin.runtime.exception import ObinReferenceError


class Reference(object):
    _immutable_fields_ = ['base_env', 'base_value', 'referenced']

    def __init__(self, base_env=None, referenced=None):
        self.base_env = base_env
        self.referenced = referenced

    def get_referenced_name(self):
        return self.referenced

    def is_unresolvable(self):
        return self.base_env is None

    def get_value(self):
        if self.is_unresolvable():
            raise ObinReferenceError(self.get_referenced_name())
        else:
            return self.base_env.get_binding_value(self.get_referenced_name())

    def put_value(self, value):
        if self.is_unresolvable():
            raise ObinReferenceError(self.get_referenced_name())
        else:
            self.base_env.set_binding(self.get_referenced_name(), value)

