from rpython.rlib import jit
from obin.objects.space import newstring, _w
from obin.runtime.environment import newenv
from obin.runtime.routine.code_routine import CodeRoutine
from obin.runtime.routine.native_routine import NativeRoutine
from obin.objects import api

def complete_native_routine(func):
    def func_wrapper(process, routine):
        result = func(process, routine)
        routine.complete(_w(result))

    return func_wrapper

def create_primitive_routine(name, primitive, args, arity):
    return NativeRoutine(name, primitive, args, arity)


def create_module_routine(code, module, _globals):
    assert _globals
    if _globals is not None:
        global_env = newenv(_globals, None)
    else:
        global_env = None
    env = newenv(module, global_env)
    return jit.promote(CodeRoutine(newstring(u"__module__"), code, env))


def create_eval_routine(code):
    from obin.runtime.environment import newenv
    obj = code.scope.create_object()
    env = newenv(obj, None)
    return jit.promote(CodeRoutine(newstring(u"__module__"), code, env))


def create_function_routine(func, args, outer_env):
    # TODO CHANGE TO PUBLIC FIELDS
    code = func._bytecode_
    scope = code.scope
    name = func._name_

    env = create_function_environment(func, scope, args, outer_env)
    return jit.promote(CodeRoutine(name, code, env))


def create_function_environment(func, scope, args, outer_env):
    from obin.runtime.environment import newenv
    from obin.objects.space import newplainobject_with_slots, newvector

    declared_args_count = scope.count_args
    is_variadic = scope.is_variadic
    args_count = api.n_length(args)

    if not is_variadic:
        if args_count < declared_args_count:
            raise RuntimeError("Wrong argument count in function call %d < %d %s" % (args_count, declared_args_count,
                                                                                     str(scope.variables.keys())))

        actual_args_count = declared_args_count
        if args_count != actual_args_count:
            raise RuntimeError("Wrong argument count in function call %s %s" %
                               (str(scope.arguments), str(args)))
    else:
        varargs_index = declared_args_count - 1
        actual_args_count = varargs_index

        if args_count < actual_args_count:
            raise RuntimeError("Wrong argument count in function call %d < %d %s" % (args_count, declared_args_count,
                                                                                     str(scope.variables.keys())))

        if args_count != actual_args_count:
            args.fold_slice_into_itself(actual_args_count)
        else:
            args.append(newvector([]))

    slots = scope.create_environment_slots(args)
    env = newenv(newplainobject_with_slots(slots), outer_env)

    fn_index = scope.fn_name_index
    if fn_index != -1:
        env.set_local(fn_index, func)

    return env
