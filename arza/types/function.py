from arza.types.root import W_Callable, W_Root
from arza.runtime.error import *
from arza.types import api, array


class W_FunctionSource(W_Root):
    def __init__(self, name, code):
        self.name = name
        self.code = code

    def _to_string_(self):
        return "<funcsource %s>" % (api.to_s(self.name))

    def _to_repr_(self):
        return self._to_string_()


class W_Function(W_Callable):
    # _immutable_fields_ = ['scope',  'is_variadic', 'arity', '_name_']

    def __init__(self, name, bytecode, env):
        self.name = name
        self.bytecode = bytecode
        scope_info = bytecode.scope
        self.arity = scope_info.arg_count
        self.is_variadic = scope_info.is_variadic
        self.env = env

    def _to_string_(self):
        # params = ",".join([api.to_native_string(p) for p in self.bytecode.scope.arguments])
        # return "fn %s(%s){ %s }" % (self._name_.value(), params, self._bytecode_.tostring())
        return "<func %s/%d>" % (api.to_s(self.name), self.arity)

    def _to_repr_(self):
        return self._to_string_()

    def _type_(self, process):
        return process.std.classes.Function

    # def __str__(self):
    #     return 'Function %s' % self._tostring_()

    def _to_routine_(self, stack, args):
        from arza.runtime.routine.routine import create_function_routine
        routine = create_function_routine(stack, self, args, self.env)
        return routine

    def _call_(self, process, args):
        length = api.length_i(args)
        if not self.is_variadic and length != self.arity:
            return throw_5(Errors.INVOKE_ERROR, space.newstring(u"Invalid count of arguments "),
                           self, space.newint(self.arity), space.newint(length), args)

        process.call_object(self, args)

    def _equal_(self, other):
        from arza.types import space
        if not space.isfunction(other):
            return False

        if not api.equal_b(self.name, other.name):
            return False

        return self.bytecode is other.bytecode


