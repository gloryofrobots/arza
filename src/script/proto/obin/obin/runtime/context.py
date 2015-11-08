from obin.objects.datastructs import Stack
from obin.runtime.environment import newenv
from rpython.rlib import jit


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
        self._args_ = args

    def routine(self):
        return self._routine_

    def fiber(self):
        assert self._routine_
        assert self._routine_.fiber
        return self._routine_.fiber

    def stack_append(self, value):
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

    def store_ref(self, symbol, index, value):
        lex_env = self.env()
        ref = lex_env.get_reference(symbol)
        if not ref:
            ref = self._get_refs(index)

        if not ref.is_unresolvable():
            ref.put_value(value)
            return

        lex_env.set_binding(symbol, value)

    def get_ref(self, symbol, index=-1):
        ## TODO pre-bind symbols, work with idndex, does not work, see test_foo19
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


@jit.unroll_safe
def initialize_environment(ctx):
    env = ctx.env()
    routine = jit.promote(ctx.routine())
    code = routine.bytecode()

    from obin.runtime.routine import BytecodeRoutine
    assert isinstance(routine, BytecodeRoutine)

    from obin.objects.object_space import newvector
    names = code.params()
    args = ctx.argv()
    rest = code.params_rest()
    nlen = len(names)
    alen = len(args)
    if alen < nlen:
        raise RuntimeError("Wrong argument count in function call %d < %d %s" % (alen, nlen, str(names)))

    for i in range(nlen):
        v = args[i]
        n = names[i]
        env.set_binding(n, v)

    if alen > nlen:
        if not rest:
            raise RuntimeError("Wrong argument count in function call %s %s" % (str(names), str(args)))
        rest_items = []
        for i in range(nlen, alen):
            rest_items.append(args[i])

        env.set_binding(rest, newvector(rest_items))


def create_object_context(routine, obj):
    from obin.runtime.environment import newobjectenv
    ctx = Context(routine.estimated_stack_size(), 0, routine, newobjectenv(obj, None), None)
    return ctx


def create_eval_context(routine):
    from obin.runtime.environment import newenv
    ctx = Context(routine.estimated_stack_size(), 0, routine, newenv(None, 0), None)
    return ctx


def create_function_context(routine, args, scope):
    from obin.runtime.environment import newenv
    stack_size = routine.estimated_stack_size()
    env_size = routine.env_size()
    ctx = Context(stack_size, env_size, routine, newenv(scope, env_size), args)
    initialize_environment(ctx)
    return ctx


def create_primitive_context(routine, args):
    stack_size = routine.estimated_stack_size()
    env_size = routine.env_size()
    ctx = Context(stack_size, env_size, routine, None, args)
    return ctx


class BlockContext(Context):
    def __init__(self, code, parent_context):
        stack_size = code.estimated_stack_size()
        Context.__init__(self, stack_size)

        code.set_context(self)
        self._parent_context_ = parent_context

        parent_env = parent_context.env()

        env_size = code.env_size()
        local_env = newenv(parent_env, env_size)

        self.set_env(local_env)

        self.declaration_binding_initialization()


class CatchContext(Context):
    def __init__(self, code, catchparam, exception_value, parent_context):
        stack_size = code.estimated_stack_size()
        Context.__init__(self, stack_size)

        env_size = code.env_size()
        self._routine_ = code
        self._parent_context_ = parent_context

        parent_env = parent_context.env()

        local_env = newenv(parent_env, env_size)
        local_env.set_binding(catchparam, exception_value)

        self.set_env(local_env)

        self.declaration_binding_initialization()
