from obin.runtime.exception import ObinReferenceError


class Reference(object):
    _immutable_fields_ = ['base_env', 'base_value', 'referenced']

    def __init__(self, env, referenced, index):
        self.env = env
        self.name = referenced
        self.index = index

    def is_unresolvable(self):
        return self.env is None

    def check(self):
        if self.is_unresolvable():
            raise ObinReferenceError(self.name)

    def get_value(self):
        self.check()
        return self.env.get_by_index(self.index)

    def put_value(self, value):
        self.check()
        if self.is_unresolvable():
            raise ObinReferenceError(self.name)
        else:
            self.env.set_by_index(self.index, value)

