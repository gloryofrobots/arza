from obin.objects.types.root import W_Callable, W_Root
from obin.runtime.error import *
from obin.objects import api
from rpython.rlib import jit


class W_FunctionSource(W_Root):
    def __init__(self, name, code):
        self.name = name
        self.code = code


class W_Function(W_Callable):
    # _immutable_fields_ = ['scope',  'is_variadic', 'arity', '_name_']

    def __init__(self, name, bytecode, scope):
        self.name = name
        self.bytecode = bytecode
        scope_info = bytecode.scope
        self.arity = scope_info.count_args
        self.is_variadic = scope_info.is_variadic
        self.scope = scope

    def _tostring_(self):
        params = ",".join([api.to_native_string(p) for p in self.bytecode.scope.arguments])
        # return "fn %s(%s){ %s }" % (self._name_.value(), params, self._bytecode_.tostring())
        return "fn %s(%s){ %s }" % (api.to_native_string(self.name), params, "...")

    def _tobool_(self):
        return True

    def _behavior_(self, process):
        return process.std.behaviors.Function

    # def __str__(self):
    #     return 'Function %s' % self._tostring_()

    def _to_routine_(self, stack, args):
        from obin.runtime.routine import create_function_routine
        routine = create_function_routine(stack, self, args, self.scope)
        return routine

    def _call_(self, process, args):
        process.call_object(self, args)


