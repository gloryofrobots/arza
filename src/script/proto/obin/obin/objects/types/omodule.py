from oroot import W_Root

class W_Module(W_Root):
    def __init__(self, name, bytecode):
        self._name = name
        self._bytecode_ = bytecode
        self._env_ = None
        self._result_ = None
        self._is_compiled_ = False
        self.init_scope()

    def _traits_(self):
        from obin.objects.space import state
        return state.traits.ModuleTraits

    def _tostring_(self):
        return self._env_._tostring_()

    def _at_(self, key):
        return self._env_._at_(key)

    def _lookup_(self, key):
        return self._env_._lookup_(key)

    def init_scope(self):
        self._env_ = self._bytecode_.scope.create_object()

    def result(self):
        return self._result_

    def set_result(self, r):
        self._result_ = r

    def bytecode(self):
        return self._bytecode_

    def scope(self):
        return self._env_

    def compile(self, _globals):
        assert not self._is_compiled_
        from obin.runtime.routine import create_module_routine

        routine = create_module_routine(self._bytecode_, self._env_, _globals)
        # print "*********"
        # for i, c in enumerate([str(c) for c in self._bytecode_.opcodes]): print i,c
        # print "*********"
        self._is_compiled_ = True
        return routine

