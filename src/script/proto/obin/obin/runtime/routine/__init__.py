from rpython.rlib import jit
from obin.types.space import isany
from obin.runtime.environment import newenv
from obin.runtime.routine.code_routine import CodeRoutine
from obin.runtime.routine.native_routine import NativeRoutine
from obin.types import api


def complete_native_routine(func):
    def func_wrapper(process, routine):
        result = func(process, routine)
        if not isany(result):
            raise RuntimeError
        assert isany(result)
        routine.complete(process, result)

    return func_wrapper


def create_native_routine(stack, name, native, args, arity):
    return NativeRoutine(stack, name, native, args, arity)


def create_origin_routine(stack, constructor, args):
    from obin.runtime.routine.origin_routine import OriginRoutine
    return OriginRoutine(stack, constructor, args)


def create_module_routine(name, stack, code, module_env, _globals):
    assert _globals
    if _globals is not None:
        global_env = newenv(_globals, None)
    else:
        global_env = None
    env = newenv(module_env, global_env)
    return jit.promote(CodeRoutine(stack, None, name, code, env))


def create_function_routine(stack, func, args, outer_env):
    code = func.bytecode
    scope = code.scope
    name = func.name

    env = create_function_environment(func, scope, args, outer_env)
    routine = jit.promote(CodeRoutine(stack, args, name, code, env))
    return routine


def create_function_environment(func, scope, args, outer_env):
    from obin.runtime.environment import newenv

    declared_args_count = scope.count_args
    args_count = api.n_length(args)

    if args_count < declared_args_count:
        raise RuntimeError("Wrong argument count in function call %d < %d %s" % (args_count, declared_args_count,
                                                                                 str(scope.variables.keys())))
    slots = scope.create_env_bindings()
    env = newenv(slots, outer_env)

    fn_index = scope.fn_name_index
    if fn_index != -1:
        env.set_local(fn_index, func)

    return env
