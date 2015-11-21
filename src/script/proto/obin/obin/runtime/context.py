from obin.objects.stack import Stack
from rpython.rlib import jit
from obin.runtime.exception import ObinReferenceError


class Context(object):
    _immutable_fields_ = ['_stack_', '_env_',
                          '_refs_', '_routine_',
                          '_args_', '_resizable_']
    # TODO why are _formal_parameters_, _w_func_ etc. required here?
    _virtualizable2_ = ['_refs_[*]']
    _settled_ = True

    def __init__(self, stack_size, refs_size, routine, env):
        name = self.__class__.__name__
        self = jit.hint(self, access_directly=True, fresh_virtualizable=True)

        self._stack_ = Stack(stack_size)
        self._routine_ = routine
        self._routine_.set_context(self)
        self._env_ = env
        self._refs_ = [None] * refs_size
        self._resizable_ = not bool(refs_size)

    def routine(self):
        return self._routine_

    def process(self):
        assert self._routine_
        assert self._routine_.process
        return self._routine_.process

    def stack_append(self, value):
        from obin.objects.object_space import isany
        assert isany(value)
        self._stack_.push(value)

    def stack_pop(self):
        return self._stack_.pop()

    def stack_top(self):
        return self._stack_.top()

    @jit.unroll_safe
    def stack_pop_n(self, n):
        return self._stack_.pop_n(n)

    @jit.unroll_safe
    def stack_pop_n_into(self, n, arr):
        return self._stack_.pop_n_into(n, arr)

    def stack_pointer(self):
        return self._stack_.pointer()

    def set_stack_pointer(self, p):
        self._stack_.set_pointer(p)

    def env(self):
        return self._env_

    def _resize_refs(self, index):
        if index >= len(self._refs_):
            self._refs_ += ([None] * (1 + index - len(self._refs_)))

    def _get_refs(self, index):
        assert index < len(self._refs_)
        assert index >= 0

        if self._resizable_:
            self._resize_refs(index)

        return self._refs_[index]

    def _set_refs(self, index, value):
        if self._resizable_:
            self._resize_refs(index)
        assert index < len(self._refs_)
        assert index >= 0
        self._refs_[index] = value

    def get_local(self, index):
        return self._env_.get_by_index(index)

    def store_local(self, index, value):
        self._env_.set_by_index(index, value)

    def store_ref(self, symbol, index, value):
        ref = self._get_refs(index)

        if ref is not None:
            ref.put_value(value)
            return

        ref = self.env().get_reference(symbol)
        if not ref:
            raise RuntimeError("Unable to store reference", symbol, index, value)

        ref.put_value(value)
        self._set_refs(index, ref)

    def get_ref(self, symbol, index=-1):
        # if index < 0:
        #     lex_env = self.env()
        #     ref = lex_env.get_reference(symbol)
        #     return ref
        ref = self._get_refs(index)

        if ref is None:
            lex_env = self.env()
            ref = lex_env.get_reference(symbol)
            if not ref:
                raise ObinReferenceError(symbol)
            self._set_refs(index, ref)

        return ref.get_value()

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
        env.set_by_index(fn_index, func)

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


# class BlockContext(Context):
#     def __init__(self, code, parent_context):
#         stack_size = code.estimated_stack_size()
#         Context.__init__(self, stack_size)
#
#         code.set_context(self)
#         self._parent_context_ = parent_context
#
#         parent_env = parent_context.env()
#
#         env_size = code.estimated_env_size()
#         local_env = newenv(parent_env, env_size)
#
#         self.set_env(local_env)
#
#         self.declaration_binding_initialization()
#
#
# class CatchContext(Context):
#     def __init__(self, code, catchparam, exception_value, parent_context):
#         stack_size = code.estimated_stack_size()
#         Context.__init__(self, stack_size)
#
#         env_size = code.estimated_env_size()
#         self._routine_ = code
#         self._parent_context_ = parent_context
#
#         parent_env = parent_context.env()
#
#         local_env = newenv(parent_env, env_size)
#         local_env.set_binding(catchparam, exception_value)
#
#         self.set_env(local_env)
#
#         self.declaration_binding_initialization()
