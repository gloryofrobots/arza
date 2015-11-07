from obin.objects.object_space import newundefined
from obin.objects.datastructs import Stack
from rpython.rlib import jit

DISTINCT = []

class ExecutionContext(object):
    _immutable_fields_ = ['_stack_', '_lexical_environment_', '_variable_environment_', '_refs_', '_code_', '_formal_parameters_', '_argument_values_', '_w_func_']  # TODO why are _formal_parameters_, _w_func_ etc. required here?
    _virtualizable2_ = ['_stack_[*]', '_stack_pointer_', '_refs_[*]']
    _settled_ = True

    def __init__(self, stack_size=1, refs_size=1):
        name =  self.__class__.__name__
        if name not in DISTINCT:
            DISTINCT.append(name)
            print "CTX", DISTINCT

        self = jit.hint(self, access_directly=True, fresh_virtualizable=True)

        self._stack_ = Stack(stack_size)
        self._code_ = None
        self.__lexical_environment = None
        self._refs_ = [None] * refs_size

    def routine(self):
        return self._code_

    def fiber(self):
        assert self._code_
        assert self._code_.fiber
        return self._code_.fiber

    def set_routine(self, r):
        assert not self._code_
        self._code_ = r

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

    def lexical_environment(self):
        return self.__lexical_environment

    def set_lexical_environment(self, env):
        self.__lexical_environment = env

    # 10.5
    @jit.unroll_safe
    def declaration_binding_initialization(self):
        from obin.objects.object_space import newundefined
        # if str(self._code_) == "function _f2 {}":
        #     x = 1

        env = self.lexical_environment()
        code = jit.promote(self._code_)

        # 4.
        if code.is_function_code():
            from obin.objects.object_space import _w
            names = code.params()
            args = self._argument_values_
            rest = code.params_rest()
            nlen = len(names)
            alen = len(args)
            if alen < nlen:
                raise RuntimeError("Wrong argument count in function call %d < %d %s" % (alen, nlen, names))

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

    def _get_refs(self, index):
        assert index < len(self._refs_)
        assert index >= 0
        return self._refs_[index]

    def _set_refs(self, index, value):
        assert index < len(self._refs_)
        assert index >= 0
        self._refs_[index] = value

    def store_ref(self, symbol, index, value):
        lex_env = self.lexical_environment()
        ref = lex_env.get_reference(symbol)
        if not ref:
            ref = self._get_refs(index)

        if not ref.is_unresolvable_reference():
            ref.put_value(value)
            return

        lex_env.set_binding(symbol, value)

    def get_ref(self, symbol, index=-1):
        ## TODO pre-bind symbols, work with idndex, does not work, see test_foo19
        if index < 0:
            lex_env = self.lexical_environment()
            ref = lex_env.get_reference(symbol)
            return ref

        ref = self._get_refs(index)

        if ref is None:
            lex_env = self.lexical_environment()
            ref = lex_env.get_reference(symbol)
            if ref.is_unresolvable_reference() is True:
                return ref
            self._set_refs(index, ref)

        return ref

    def forget_ref(self, symbol, index):
        self._set_refs(index, None)


class _DynamicExecutionContext(ExecutionContext):
    def _get_refs(self, index):
        from obin.utils import tb
        # if index > len(self._refs_):
        #     tb("BAD INDEX")

        # assert index < len(self._refs_)
        self._resize_refs(index)
        return self._refs_[index]

    def _set_refs(self, index, value):
        self._resize_refs(index)
        self._refs_[index] = value

    def _resize_refs(self, index):
        if index >= len(self._refs_):
            self._refs_ += ([None] * (1 + index - len(self._refs_)))


class ObjectExecutionContext(_DynamicExecutionContext):
    def __init__(self, code, obj):
        stack_size = code.estimated_stack_size()

        _DynamicExecutionContext.__init__(self, stack_size)

        self._code_ = code

        from obin.runtime.environment import newobjectenv
        env = newobjectenv(obj, None)
        self.set_lexical_environment(env)
        self.declaration_binding_initialization()


class EvalExecutionContext(_DynamicExecutionContext):
    def __init__(self, code, calling_context=None):
        stack_size = code.estimated_stack_size()

        _DynamicExecutionContext.__init__(self, stack_size)
        self._code_ = code

        # if not calling_context:
        #     raise NotImplementedError()

        from obin.runtime.environment import newenv
        strict_var_env = newenv(self.lexical_environment(), 0)
        self.set_lexical_environment(strict_var_env)

        self.declaration_binding_initialization()


class FunctionExecutionContext(ExecutionContext):
    _immutable_fields_ = ['_scope_', '_calling_context_']

    def __init__(self, code, argv=[], scope=None, w_func=None):
        stack_size = code.estimated_stack_size()
        env_size = code.env_size() + 1  # neet do add one for the arguments object

        ExecutionContext.__init__(self, stack_size, env_size)

        self._code_ = code
        self._argument_values_ = argv
        self._scope_ = scope
        self._w_func_ = w_func
        self._calling_context_ = None

        from obin.runtime.environment import newenv
        env = newenv(scope, env_size)
        self.set_lexical_environment(env)

        self.declaration_binding_initialization()

    def argv(self):
        return self._argument_values_

class BlockExecutionContext(_DynamicExecutionContext):
    def __init__(self, code, parent_context):
        stack_size = code.estimated_stack_size()
        _DynamicExecutionContext.__init__(self, stack_size)

        code.set_context(self)
        self._parent_context_ = parent_context

        parent_env = parent_context.lexical_environment()

        from obin.runtime.environment import newenv
        env_size = code.env_size() + 1  # neet do add one for the arguments object
        local_env = newenv(parent_env, env_size)

        self.set_lexical_environment(local_env)

        self.declaration_binding_initialization()

class CatchExecutionContext(_DynamicExecutionContext):
    def __init__(self, code, catchparam, exception_value, parent_context):
        stack_size = code.estimated_stack_size()
        _DynamicExecutionContext.__init__(self, stack_size)

        env_size = code.env_size() + 1  # neet do add one for the arguments object
        self._code_ = code
        self._parent_context_ = parent_context

        parent_env = parent_context.lexical_environment()

        from obin.runtime.environment import newenv
        local_env = newenv(parent_env, env_size)
        local_env.set_binding(catchparam, exception_value)

        self.set_lexical_environment(local_env)

        self.declaration_binding_initialization()

