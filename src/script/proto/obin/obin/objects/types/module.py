from root import W_Root
class W_Module(W_Root):
    def __init__(self, name, bytecode):
        self._name = name
        self._bytecode_ = bytecode
        self._object_ = None
        self._result_ = None
        self._is_compiled_ = False
        self.init_scope()

    def _traits_(self):
        from obin.objects.object_space import object_space
        return object_space.traits.ModuleTraits

    def init_scope(self):
        self._object_ = self._bytecode_.scope.create_object()

    def result(self):
        return self._result_

    def set_result(self, r):
        self._result_ = r

    def bytecode(self):
        return self._bytecode_

    def scope(self):
        return self._object_

    def compile(self, _globals):
        assert not self._is_compiled_
        from obin.runtime.routine import create_module_routine

        routine = create_module_routine(self._bytecode_, self._object_, _globals)
        # print "*********"
        # for i, c in enumerate([str(c) for c in self._bytecode_.opcodes]): print i,c
        # print "*********"
        self._is_compiled_ = True
        return routine

