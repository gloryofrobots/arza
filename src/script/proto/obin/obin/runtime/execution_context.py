from obin.objects.datastructs import Stack
from obin.runtime.environment import newenv
from rpython.rlib import jit

DISTINCT = []

class ExecutionContext(object):
    _immutable_fields_ = ['_stack_', '_lexical_environment_',
                          '_refs_', '_routine_', '_formal_parameters_',
                          '_argument_values_', '_w_func_']
                          # TODO why are _formal_parameters_, _w_func_ etc. required here?
    _virtualizable2_ = ['_stack_[*]', '_stack_pointer_', '_refs_[*]']
    _settled_ = True

    def __init__(self, stack_size=1, refs_size=0):
        name = self.__class__.__name__
        if name not in DISTINCT:
            DISTINCT.append(name)
            print "CTX", DISTINCT

        self = jit.hint(self, access_directly=True, fresh_virtualizable=True)

        self._stack_ = Stack(stack_size)
        self._routine_ = None
        self._env_ = None
        self._refs_ = [None] * refs_size
        self.__resizable = not bool(refs_size)

    def routine(self):
        return self._routine_

    def fiber(self):
        assert self._routine_
        assert self._routine_.fiber
        return self._routine_.fiber

    def set_routine(self, r):
        assert not self._routine_
        self._routine_ = r

    def stack_append(self, value):
        self._stack_.push(value)

    def stack_pop(self):
        return self._stack_.pop()

    def stack_top(self):
        return self._stack_.top()

    @jit.unroll_safe
    def stack_pop_n(self, n):
        return self._stack_.pop_n(n)

    def stack_pointer(self):
        return self._stack_.pointer()

    def set_stack_pointer(self, p):
        self._stack_.set_pointer(p)

    def env(self):
        return self._env_

    def set_env(self, env):
        self._env_ = env

    # 10.5
    @jit.unroll_safe
    def declaration_binding_initialization(self):
        env = self.env()
        code = jit.promote(self._routine_)

        # 4.
        if code.is_function_code():
            from obin.objects.object_space import _w
            names = code.params()
            args = self._argument_values_
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

                env.set_binding(rest, _w(rest_items))

        # 5.
        func_declarations = code.functions()
        for fn in func_declarations:
            fo = None
            env.set_binding(fn, fo)

    def is_resizable(self):
        return self.__resizable

    def _resize_refs(self, index):
        if index >= len(self._refs_):
            self._refs_ += ([None] * (1 + index - len(self._refs_)))

    def _get_refs(self, index):
        if self.is_resizable():
            self._resize_refs(index)
        assert index < len(self._refs_)
        assert index >= 0
        return self._refs_[index]

    def _set_refs(self, index, value):
        if self.is_resizable():
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

    def forget_ref(self, symbol, index):
        self._set_refs(index, None)



class ObjectExecutionContext(ExecutionContext):
    def __init__(self, code, obj):
        stack_size = code.estimated_stack_size()

        ExecutionContext.__init__(self, stack_size)

        self._routine_ = code

        from obin.runtime.environment import newobjectenv
        env = newobjectenv(obj, None)
        self.set_env(env)
        self.declaration_binding_initialization()


class EvalExecutionContext(ExecutionContext):
    def __init__(self, code):
        stack_size = code.estimated_stack_size()

        ExecutionContext.__init__(self, stack_size)
        self._routine_ = code

        strict_var_env = newenv(self.env(), 0)
        self.set_env(strict_var_env)

        self.declaration_binding_initialization()


class FunctionExecutionContext(ExecutionContext):
    _immutable_fields_ = ['_scope_', '_calling_context_']

    def __init__(self, routine, argv=[], scope=None, w_func=None):
        stack_size = routine.estimated_stack_size()
        env_size = routine.env_size() + 1  # neet do add one for the arguments object

        ExecutionContext.__init__(self, stack_size, env_size)

        self._routine_ = routine
        self._argument_values_ = argv
        # self._scope_ = scope
        # self._w_func_ = w_func
        # self._calling_context_ = None

        env = newenv(scope, env_size)
        self.set_env(env)

        self.declaration_binding_initialization()

    def argv(self):
        return self._argument_values_

class BlockExecutionContext(ExecutionContext):
    def __init__(self, code, parent_context):
        stack_size = code.estimated_stack_size()
        ExecutionContext.__init__(self, stack_size)

        code.set_context(self)
        self._parent_context_ = parent_context

        parent_env = parent_context.env()

        env_size = code.env_size() + 1  # neet do add one for the arguments object
        local_env = newenv(parent_env, env_size)

        self.set_env(local_env)

        self.declaration_binding_initialization()

class CatchExecutionContext(ExecutionContext):
    def __init__(self, code, catchparam, exception_value, parent_context):
        stack_size = code.estimated_stack_size()
        ExecutionContext.__init__(self, stack_size)

        env_size = code.env_size() + 1  # neet do add one for the arguments object
        self._routine_ = code
        self._parent_context_ = parent_context

        parent_env = parent_context.env()

        local_env = newenv(parent_env, env_size)
        local_env.set_binding(catchparam, exception_value)

        self.set_env(local_env)

        self.declaration_binding_initialization()

