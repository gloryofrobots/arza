
class Context(object):
    _immutable_fields_ = ['stack', '_env_',
                          '_routine_',
                          '_args_', '_resizable_']
    _settled_ = True

    def __init__(self, stack_size, refs_size, routine, env):
        self = jit.hint(self, access_directly=True, fresh_virtualizable=True)

        self._routine_ = routine
        self._routine_.set_context(self)

    def routine(self):
        return self._routine_

    def process(self):
        assert self._routine_
        assert self._routine_.process
        return self._routine_.process


