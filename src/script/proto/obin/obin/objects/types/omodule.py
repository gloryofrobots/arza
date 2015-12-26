from oroot import W_Root


class W_Module(W_Root):
    def __init__(self, name, bytecode, builtins):
        self.name = name
        self.bytecode = bytecode
        self.result = None
        self.is_compiled = False
        self.builtins = builtins
        self.env = self.bytecode.scope.create_object()

    def _traits_(self):
        from obin.objects.space import stdlib
        return stdlib.traits.ModuleTraits

    def _tostring_(self):
        return self.env._tostring_()

    def _at_(self, key):
        return self.env._at_(key)

    def _lookup_(self, key):
        return self.env._lookup_(key)


def compile_module(module):
    assert not module.is_compiled
    from obin.runtime.routine import create_module_routine

    routine = create_module_routine(module.bytecode, module.env, module.builtins)
    # print "*********"
    # for i, c in enumerate([str(c) for c in self._bytecode_.opcodes]): print i,c
    # print "*********"
    module.is_compiled = True
    return routine
