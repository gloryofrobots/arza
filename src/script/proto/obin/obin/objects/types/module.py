from obin.objects.types.root import W_Root


class W_Module(W_Root):
    def __init__(self, name, bytecode, builtins):
        self.name = name
        self.bytecode = bytecode
        self.is_compiled = False
        self.builtins = builtins
        self.env = self.bytecode.scope.create_env_bindings()
        self.result = None

    def _behavior_(self, process):
        return process.std.behaviors.Module

    def _tostring_(self):
        return self.env._tostring_()

    def _at_(self, key):
        return self.env._at_(key)

    def _to_routine_(self, stack, args):
        if self.is_compiled:
            raise RuntimeError("Module Already compiled")

        from obin.runtime.routine import create_module_routine

        routine = create_module_routine(self.name, stack, self.bytecode, self.env, self.builtins)
        # print "*********"
        # for i, c in enumerate([str(c) for c in self._bytecode_.opcodes]): print i,c
        # print "*********"
        self.is_compiled = True
        return routine
