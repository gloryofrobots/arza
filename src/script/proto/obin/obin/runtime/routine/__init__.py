from obin.misc.platform import jit
from obin.types.space import isany
from obin.runtime import error
from obin.runtime.routine.code_routine import CodeRoutine
from obin.runtime.routine.native_routine import NativeRoutine
from obin.types import api, space

def complete_or_interrupt_native_routine(func):
    def func_wrapper(process, routine):
        result = func(process, routine)
        assert isany(result)
        if space.isinterrupt(result):
            return
        if not routine.is_closed():
            routine.complete(process, result)

    return func_wrapper

def complete_native_routine(func):
    def func_wrapper(process, routine):
        result = func(process, routine)
        if not isany(result):
            raise RuntimeError((result, func))
        assert isany(result)
        if not routine.is_closed():
            routine.complete(process, result)

    return func_wrapper


def create_native_routine(stack, name, native, args, arity):
    return NativeRoutine(stack, name, native, args, arity)


# TODO THIS LEFT FROM ORIGIN ROUTINE REMAKE IT AS LAZY
def create_lazy_routine(stack, constructor, args):
    from obin.runtime.routine.lazy_routine import LazyRoutine
    return LazyRoutine(stack, constructor, args)


def create_module_routine(name, stack, code, env):
    return jit.promote(CodeRoutine(space.newnil(), stack, None, name, code, env))


def create_function_routine(stack, func, args, outer_env):
    code = func.bytecode
    scope = code.scope
    name = func.name

    env = create_function_environment(func, scope, args, outer_env)
    routine = jit.promote(CodeRoutine(func, stack, args, name, code, env))
    return routine


def create_function_environment(func, scope, args, outer_env):

    declared_args_count = scope.count_args if not scope.is_variadic else scope.count_args - 1
    args_count = api.length_i(args)

    if not scope.is_variadic:
        if args_count != declared_args_count:
            return error.throw_4(error.Errors.INVALID_ARG_COUNT,
                                 space.newint(args_count), space.newstring(u"!="), space.newint(declared_args_count),
                                 func.name)
    if args_count < declared_args_count:
        return error.throw_4(error.Errors.INVALID_ARG_COUNT,
                             space.newint(args_count), space.newstring(u"<"), space.newint(declared_args_count),
                             func.name)

    env = space.newenv(func.name, scope, outer_env)
    return env
