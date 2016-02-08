from obin.types.root import W_Any, W_Callable
from obin.types import space, api
from obin.runtime import error


def create_environment(process, source, parent_env):
    if source.env:
        return source.env

    modulefunc = W_ModuleFunction(source.name, source.bytecode, parent_env)
    process.subprocess(modulefunc, space.newnil())

    source.env = modulefunc.env
    return source.env


class W_ModuleFunction(W_Callable):
    def __init__(self, name, bytecode, parent_env):
        self.name = name
        self.bytecode = bytecode
        self.parent_env = parent_env

        bindings = self.bytecode.scope.create_env_bindings()
        self.env = space.newenv(bindings, parent_env)

    def _to_routine_(self, stack, args):
        from obin.runtime.routine import create_module_routine
        routine = create_module_routine(self.name, stack, self.bytecode, self.env)
        return routine


class W_Module(W_Any):
    def __init__(self, name, bytecode, env):
        self.name = name
        self.bytecode = bytecode
        self.env = env

    def _at_(self, key):
        return self.env._at_(key)

    def _put_(self, k, v):
        return self.env._put_(k, v)

    def _tostring_(self):
        if not self.env:
            return "<module %s>" % api.to_s(self.name)
        if not self.name:
            return "<module>"
        return "<module %s where %s>" % (api.to_s(self.name), api.to_s(self.env))
