from obin.utils import StackMixin
from obin.objects.object_space import newundefined
from rpython.rlib import jit


class ExecutionContext(StackMixin):
    _immutable_fields_ = ['_stack_', '_this_binding_', '_lexical_environment_', '_variable_environment_', '_refs_', '_code_', '_formal_parameters_', '_argument_values_', '_w_func_']  # TODO why are _formal_parameters_, _w_func_ etc. required here?
    _virtualizable2_ = ['_stack_[*]', '_stack_pointer_', '_refs_[*]']
    _settled_ = True

    def __init__(self, stack_size=1, refs_size=1):
        self = jit.hint(self, access_directly=True, fresh_virtualizable=True)
        self._code_ = None
        self._lexical_environment_ = None
        self._variable_environment_ = None
        self._this_binding_ = None
        self._refs_ = [None] * refs_size
        self._init_stack_(stack_size)

    def routine(self):
        return self._code_

    def stack_append(self, value):
        self._stack_append(value)

    def stack_pop(self):
        return self._stack_pop()

    def stack_top(self):
        return self._stack_top()

    @jit.unroll_safe
    def stack_pop_n(self, n):
        if n < 1:
            return []

        r = []
        i = n
        while i > 0:
            i -= 1
            e = self._stack_pop()
            r = [e] + r

        return r

    def this_binding(self):
        return self._this_binding_

    def variable_environment(self):
        return self._variable_environment_

    def lexical_environment(self):
        return self._lexical_environment_

    def set_lexical_environment(self, lex_env):
        self._lexical_environment_ = lex_env

    # 10.5
    @jit.unroll_safe
    def declaration_binding_initialization(self):
        from obin.objects.object_space import newundefined

        env = self._variable_environment_.environment_record
        code = jit.promote(self._code_)

        # 4.
        if code.is_function_code():
            names = code.params()
            n = 0
            args = self._argument_values_

            arg_count = len(args)
            for arg_name in names:
                n += 1
                if n > arg_count:
                    v = newundefined()
                else:
                    v = args[n - 1]
                env.set_binding(arg_name, v)

        # 5.
        func_declarations = code.functions()
        for fn in func_declarations:
            fo = None
            func_already_declared = env.has_binding(fn)
            env.set_binding(fn, fo)

        arguments_already_declared = env.has_binding(u'arguments')
        # 7.
        if code.is_function_code() and arguments_already_declared is False:
            from obin.objects.object import W_Arguments
            # TODO get calling W_Function
            func = self._w_func_
            arguments = self._argument_values_
            names = code.params()
            args_obj = W_Arguments(func, names, arguments, env)

            env.set_binding(u'arguments', args_obj)

        # 8.
        var_declarations = code.variables()
        for dn in var_declarations:
            env.set_binding(dn, newundefined())

    def _get_refs(self, index):
        assert index < len(self._refs_)
        assert index >= 0
        return self._refs_[index]

    def _set_refs(self, index, value):
        assert index < len(self._refs_)
        assert index >= 0
        self._refs_[index] = value

    def get_ref(self, symbol, index=-1):
        ## TODO pre-bind symbols, work with idndex, does not work, see test_foo19
        if index < 0:
            lex_env = self.lexical_environment()
            ref = lex_env.get_identifier_reference(symbol)
            return ref

        ref = self._get_refs(index)

        if ref is None:
            lex_env = self.lexical_environment()
            ref = lex_env.get_identifier_reference(symbol)
            if ref.is_unresolvable_reference() is True:
                return ref
            self._set_refs(index, ref)

        return ref

    def forget_ref(self, symbol, index):
        self._set_refs(index, None)


class _DynamicExecutionContext(ExecutionContext):
    def __init__(self, stack_size):
        ExecutionContext.__init__(self, stack_size)
        self._dyn_refs_ = [None]

    def _get_refs(self, index):
        self._resize_refs(index)
        return self._dyn_refs_[index]

    def _set_refs(self, index, value):
        self._resize_refs(index)
        self._dyn_refs_[index] = value

    def _resize_refs(self, index):
        if index >= len(self._dyn_refs_):
            self._dyn_refs_ += ([None] * (1 + index - len(self._dyn_refs_)))


class ObjectExecutionContext(_DynamicExecutionContext):
    def __init__(self, code, global_object):
        stack_size = code.estimated_stack_size()

        _DynamicExecutionContext.__init__(self, stack_size)

        self._code_ = code

        from obin.runtime.lexical_environment import ObjectEnvironment
        localEnv = ObjectEnvironment(global_object)
        self._lexical_environment_ = localEnv
        self._variable_environment_ = localEnv
        self._this_binding_ = global_object

        self.declaration_binding_initialization()


class EvalExecutionContext(_DynamicExecutionContext):
    def __init__(self, code, calling_context=None):
        stack_size = code.estimated_stack_size()

        _DynamicExecutionContext.__init__(self, stack_size)
        self._code_ = code

        if not calling_context:
            raise NotImplementedError()

        from obin.runtime.lexical_environment import DeclarativeEnvironment
        strict_var_env = DeclarativeEnvironment(self._lexical_environment_, 0)
        self._variable_environment_ = strict_var_env
        self._lexical_environment_ = strict_var_env

        self.declaration_binding_initialization()


class FunctionExecutionContext(ExecutionContext):
    _immutable_fields_ = ['_scope_', '_calling_context_']

    def __init__(self, code, formal_parameters=[], argv=[], this=newundefined(), scope=None, w_func=None):
        stack_size = code.estimated_stack_size()
        env_size = code.env_size() + 1  # neet do add one for the arguments object

        ExecutionContext.__init__(self, stack_size, env_size)

        self._code_ = code
        self._argument_values_ = argv
        self._scope_ = scope
        self._w_func_ = w_func
        self._calling_context_ = None

        from obin.runtime.lexical_environment import DeclarativeEnvironment
        localEnv = DeclarativeEnvironment(scope, env_size)
        self._lexical_environment_ = localEnv
        self._variable_environment_ = localEnv

        self._this_binding_ = this

        self.declaration_binding_initialization()

    def argv(self):
        return self._argument_values_


class SubExecutionContext(_DynamicExecutionContext):
    def __init__(self, parent):
        _DynamicExecutionContext.__init__(self, 0)
        self._parent_context_ = parent

    def stack_append(self, value):
        self._parent_context_.stack_append(value)

    def stack_pop(self):
        return self._parent_context_.stack_pop()

    def stack_top(self):
        return self._parent_context_.stack_top()

    def stack_pop_n(self, n):
        return self._parent_context_.stack_pop_n(n)

    def this_binding(self):
        return self._parent_context_.this_binding()


class WithExecutionContext(SubExecutionContext):
    def __init__(self, code, expr_obj, parent_context):
        SubExecutionContext.__init__(self, parent_context)
        self._code_ = code
        self._expr_obj_ = expr_obj
        self._dynamic_refs = []

        from obin.runtime.lexical_environment import ObjectEnvironment
        parent_environment = parent_context.lexical_environment()
        local_env = ObjectEnvironment(expr_obj, outer_environment=parent_environment)
        local_env.environment_record.provide_this = True

        self._lexical_environment_ = local_env
        self._variable_environment_ = local_env

        self.declaration_binding_initialization()


class CatchExecutionContext(_DynamicExecutionContext):
    def __init__(self, code, catchparam, exception_value, parent_context):
        self._code_ = code
        self._parent_context_ = parent_context

        stack_size = code.estimated_stack_size()
        env_size = code.env_size() + 1  # neet do add one for the arguments object

        _DynamicExecutionContext.__init__(self, stack_size)

        parent_env = parent_context.lexical_environment()

        from obin.runtime.lexical_environment import DeclarativeEnvironment
        local_env = DeclarativeEnvironment(parent_env, env_size)
        local_env_rec = local_env.environment_record
        local_env_rec.set_binding(catchparam, exception_value)

        self._lexical_environment_ = local_env
        self._variable_environment_ = local_env

        self.declaration_binding_initialization()

    def this_binding(self):
        return self._parent_context_.this_binding()
