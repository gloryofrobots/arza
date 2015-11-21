from obin.objects.stack import Stack
from obin.runtime.environment import newenv
from rpython.rlib import jit
from obin.runtime.exception import ObinReferenceError


class Context(object):
    _immutable_fields_ = ['_stack_', '_env_',
                          '_refs_', '_routine_',
                          '_args_', '_resizable_']
    # TODO why are _formal_parameters_, _w_func_ etc. required here?
    _virtualizable2_ = ['_refs_[*]']
    _settled_ = True

    def __init__(self, stack_size, refs_size, routine, env, args):
        name = self.__class__.__name__
        self = jit.hint(self, access_directly=True, fresh_virtualizable=True)

        self._stack_ = Stack(stack_size)
        self._routine_ = routine
        self._routine_.set_context(self)
        self._env_ = env
        self._refs_ = [None] * refs_size
        self._resizable_ = not bool(refs_size)
        if args is not None:
            self._args_ = args.values()
        else:
            self._args_ = None

    def routine(self):
        return self._routine_

    def process(self):
        assert self._routine_
        assert self._routine_.process
        return self._routine_.process

    def stack_append(self, value):
        from obin.objects.object_space import isany
        if not isany(value):
            print value
        assert isany(value)
        self._stack_.push(value)

    def stack_pop(self):
        return self._stack_.pop()

    def stack_top(self):
        return self._stack_.top()

    def argv(self):
        return self._args_

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
        if self._resizable_:
            self._resize_refs(index)
        assert index < len(self._refs_)
        assert index >= 0
        return self._refs_[index]

    def _set_refs(self, index, value):
        if self._resizable_:
            self._resize_refs(index)
        assert index < len(self._refs_)
        assert index >= 0
        self._refs_[index] = value

    def store_local(self, index, value):
        self._env_.set_by_index(index, value)

    def store_ref(self, symbol, index, value):
        lex_env = self.env()
        ref = lex_env.get_reference(symbol)
        if not ref:
            ref = self._get_refs(index)

        if not ref.is_unresolvable():
            ref.put_value(value)
            return

        raise RuntimeError("Unable to store reference", symbol, index, value)

    def get_local(self, index):
        return self._env_.get_by_index(index)

    def get_ref(self, symbol, index=-1):
        if index < 0:
            lex_env = self.env()
            ref = lex_env.get_reference(symbol)
            return ref

        ref = self._get_refs(index)

        if ref is None:
            lex_env = self.env()
            ref = lex_env.get_reference(symbol)
            if ref.is_unresolvable() is True:
                return ref
            self._set_refs(index, ref)

        return ref

def create_environment(func, routine, args, outer_env):
    from obin.runtime.environment import newobjectenv
    from obin.objects.object_space import newvector
    from obin.runtime.routine import BytecodeRoutine
    from obin.objects.object_space import newplainobject_with_slots

    assert isinstance(routine, BytecodeRoutine)

    code = routine.bytecode()
    scope = code.scope
    declared_args_count = scope.count_args
    is_variadic = scope.is_variadic
    args_count = args.length()

    if args_count < declared_args_count:
        raise RuntimeError("Wrong argument count in function call %d < %d %s" % (args_count, declared_args_count,
                                                                                 str(scope.variables.keys())))
    if not is_variadic:
        actual_args_count = declared_args_count
        if args_count != actual_args_count:
            raise RuntimeError("Wrong argument count in function call %s %s" %
                               (str(scope.variables.keys()), str(args)))
    else:
        varargs_index = declared_args_count - 1
        actual_args_count = varargs_index

        if args_count != actual_args_count:
            args.fold_slice_into_itself(actual_args_count)

    fn_index = scope.fn_name_index
    if fn_index == -1:
        return

    slots = scope.create_environment_slots(args.values())
    env = newobjectenv(newplainobject_with_slots(slots), outer_env)

    env.set_by_index(fn_index, func)
    return env


def create_object_context(routine, obj, _globals):
    from obin.runtime.environment import newobjectenv
    if _globals is not None:
        _globals = newobjectenv(_globals, None)

    from obin.runtime.environment import newobjectenv
    ctx = Context(routine.estimated_stack_size(), routine.estimated_refs_count(), routine, newobjectenv(obj, _globals), None)
    return ctx


def create_function_context(func, routine, args, scope):
    routine = jit.promote(routine)
    stack_size = routine.estimated_stack_size()
    refs_size = routine.estimated_refs_count()

    env = create_environment(func, routine, args, scope)
    ctx = Context(stack_size, refs_size, routine, env, args)
    return ctx


def create_primitive_context(routine, args):
    stack_size = routine.estimated_stack_size()
    refs_size = routine.estimated_refs_count()
    ctx = Context(stack_size, refs_size, routine, None, args)
    return ctx


def create_eval_context(routine):
    from obin.runtime.environment import newobjectenv
    obj = routine.bytecode().scope.create_object()
    ctx = Context(routine.estimated_stack_size(), routine.estimated_refs_count(),
                  routine, newobjectenv(obj, None), None)
    return ctx


class BlockContext(Context):
    def __init__(self, code, parent_context):
        stack_size = code.estimated_stack_size()
        Context.__init__(self, stack_size)

        code.set_context(self)
        self._parent_context_ = parent_context

        parent_env = parent_context.env()

        env_size = code.estimated_env_size()
        local_env = newenv(parent_env, env_size)

        self.set_env(local_env)

        self.declaration_binding_initialization()


class CatchContext(Context):
    def __init__(self, code, catchparam, exception_value, parent_context):
        stack_size = code.estimated_stack_size()
        Context.__init__(self, stack_size)

        env_size = code.estimated_env_size()
        self._routine_ = code
        self._parent_context_ = parent_context

        parent_env = parent_context.env()

        local_env = newenv(parent_env, env_size)
        local_env.set_binding(catchparam, exception_value)

        self.set_env(local_env)

        self.declaration_binding_initialization()
# @jit.unroll_safe
# def initialize_environment(func, ctx):
#     env = ctx.env()
#     routine = jit.promote(ctx.routine())
#     code = routine.bytecode()
#
#     from obin.runtime.routine import BytecodeRoutine
#     assert isinstance(routine, BytecodeRoutine)
#
#     from obin.objects.object_space import newvector
#     scope = code.scope
#     declared_args_count = scope.count_args
#     is_variadic = scope.is_variadic
#     args = ctx.argv()
#     args_count = len(args)
#
#     if args_count < declared_args_count:
#         raise RuntimeError("Wrong argument count in function call %d < %d %s" % (args_count, declared_args_count,
#                                                                                  str(scope.variables.keys())))
#     if not is_variadic:
#         actual_args_count = declared_args_count
#         if args_count != actual_args_count:
#             raise RuntimeError("Wrong argument count in function call %s %s" %
#                                (str(scope.variables.keys()), str(args)))
#     else:
#         varargs_index = declared_args_count - 1
#         actual_args_count = varargs_index
#
#         rest_items = []
#         if args_count != actual_args_count:
#             rest_items = []
#             for i in range(actual_args_count, args_count):
#                 rest_items.append(args[i])
#
#         env.set_by_index(varargs_index, newvector(rest_items))
#
#     for i in xrange(actual_args_count):
#         v = args[i]
#         env.set_by_index(i, v)
#
#     fn_index = scope.fn_name_index
#     if fn_index == -1:
#         return
#
#     env.set_by_index(fn_index, func)
