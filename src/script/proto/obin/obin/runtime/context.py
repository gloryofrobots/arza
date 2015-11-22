from rpython.rlib import jit
from obin.objects.stack import Stack
from obin.runtime.reference import References


class Context(object):
    _immutable_fields_ = ['stack', '_env_',
                          '_routine_',
                          '_args_', '_resizable_']
    _settled_ = True

    def __init__(self, stack_size, refs_size, routine, env):
        self = jit.hint(self, access_directly=True, fresh_virtualizable=True)

        self._routine_ = routine
        self._routine_.set_context(self)
        self.env = env
        self.stack = Stack(stack_size)
        self.refs = References(env, refs_size)

    def routine(self):
        return self._routine_

    def process(self):
        assert self._routine_
        assert self._routine_.process
        return self._routine_.process


def create_function_environment(func, routine, args, outer_env):
    from obin.runtime.environment import newenv
    from obin.runtime.routine import BytecodeRoutine
    from obin.objects.object_space import newplainobject_with_slots, newvector

    assert isinstance(routine, BytecodeRoutine)

    code = routine.bytecode()
    scope = code.scope
    declared_args_count = scope.count_args
    is_variadic = scope.is_variadic
    args_count = args.length()

    if not is_variadic:
        if args_count < declared_args_count:
            raise RuntimeError("Wrong argument count in function call %d < %d %s" % (args_count, declared_args_count,
                                                                                     str(scope.variables.keys())))

        actual_args_count = declared_args_count
        if args_count != actual_args_count:
            raise RuntimeError("Wrong argument count in function call %s %s" %
                               (str(scope.variables.keys()), str(args)))
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


def create_object_context(routine, obj, _globals):
    from obin.runtime.environment import newenv
    if _globals is not None:
        _globals = newenv(_globals, None)

    from obin.runtime.environment import newenv
    ctx = Context(routine.estimated_stack_size(), routine.estimated_refs_count(),
                  routine, newenv(obj, _globals))
    return ctx


def create_function_context(func, routine, args, scope):
    routine = jit.promote(routine)
    stack_size = routine.estimated_stack_size()
    refs_size = routine.estimated_refs_count()

    env = create_function_environment(func, routine, args, scope)
    ctx = Context(stack_size, refs_size, routine, env)
    return ctx


def create_eval_context(routine):
    from obin.runtime.environment import newenv
    obj = routine.bytecode().scope.create_object()
    ctx = Context(routine.estimated_stack_size(), routine.estimated_refs_count(),
                  routine, newenv(obj, None))
    return ctx
