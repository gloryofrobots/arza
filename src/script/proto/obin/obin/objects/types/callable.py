from root import W_Root
from obin.runtime.exception import *
from obin.objects import api
from rpython.rlib import jit

class W_Function(W_Root):
    _type_ = 'function'
    _immutable_fields_ = ['_type_',  'scope',  'is_variadic', 'arity', '_name_']

    def __init__(self, name, bytecode, scope):
        super(W_Function, self).__init__()
        self._name_ = name
        self._bytecode_ = bytecode
        scope_info = bytecode.scope
        self.arity = scope_info.count_args
        self.is_variadic = scope_info.is_variadic
        self.scope = scope

    def _tostring_(self):
        params = ",".join([str(p.value()) for p in self._bytecode_.scope.arguments])

        return "fn %s(%s){ %s }" % (self._name_.value(), params, self._bytecode_.tostring())

    def _tobool_(self):
        return True

    def _traits_(self):
        from obin.objects.object_space import object_space
        return object_space.traits.FunctionTraits

    # def __str__(self):
    #     return 'Function %s' % self._tostring_()

    def create_routine(self, args):
        from obin.runtime.routine import create_function_routine
        routine = create_function_routine(self, args, self.scope)
        return routine

    def _call_(self, routine, args):
        assert routine
        routine.process.call_object(self, routine, args)


class W_Primitive(W_Root):
    _type_ = 'native'
    _immutable_fields_ = ['_type_', '_extensible_', '_scope_', '_params_[*]', '_function_']

    def __init__(self, name, function, arity):
        super(W_Primitive, self).__init__()
        self._name_ = name
        self._function_ = function
        self.arity = arity

    def _tostring_(self):
        return "function %s {[native code]}" % self._name_.value()

    def _tobool_(self):
        return True

    def _traits_(self):
        from obin.objects.object_space import object_space
        return object_space.traits.PrimitiveTraits

    def create_routine(self, args):
        from obin.runtime.routine import create_primitive_routine

        routine = create_primitive_routine(self._name_, self._function_, args, self.arity)

        routine = jit.promote(routine)
        return routine

    def _call_(self, routine, args):
        assert routine
        if self.arity != -1 and args.length() != self.arity:
            raise ObinRuntimeError(u"Invalid primitive call wrong count of arguments %d != %d"
                                   % (args.length(), self.arity))

        routine.process.call_object(self, routine, args)

class W_CoroutineIterator(W_Root):
    def __init__(self, coroutine):
        self._coroutine_ = coroutine

    def _tobool_(self):
        return self._coroutine_.is_accessible()

    def _next_(self):
        from obin.objects.object_space import object_space, newundefined, newinterrupt
        process = object_space.interpreter.process
        routine = process.routine
        self._coroutine_._call_(routine, None)
        return newinterrupt()

    def _tostring_(self):
        return "CoroutineIterator"


class W_CoroutineYield(W_Root):
    def __init__(self, coroutine):
        self._coroutine_ = coroutine
        self._receiver_ = None

    def coroutine(self):
        return self._coroutine_

    def set_receiver(self, continuation):
        self._receiver_ = continuation

    def _tostring_(self):
        return "fn coroutine.yield {[native code]}"

    def _tobool_(self):
        return True

    def _call_(self, routine, args):
        if not self._coroutine_.is_accessible():
            raise ObinRuntimeError(u"Can not yield from coroutine")

        assert routine
        self._coroutine_.set_receiver(routine)

        # TODO THIS IS WRONG
        value = args.at(0)
        routine.process.yield_to_routine(self._receiver_, routine, value)



class W_Coroutine(W_Root):
    _type_ = 'native'
    _immutable_fields_ = ['_function_']

    def __init__(self, function):
        super(W_Coroutine, self).__init__()
        self._function_ = function
        self._routine_ = None
        self._receiver_ = None
        self._yield_ = None

    def is_accessible(self):
        return self._routine_ is None or not self._routine_.is_closed()

    def function(self):
        return self._function_

    def set_receiver(self, co):
        # from obin.runtime.process import check_continuation_consistency
        # if self._receiver_:
        #     check_continuation_consistency(self._receiver_, co)
        self._receiver_ = co

    def _tostring_(self):
        return "fn coroutine {[native code]}"

    def _tobool_(self):
        return True

    def _lookup_(self, k):
        from obin.objects.object_space import object_space
        return api.at(object_space.traits.Coroutine, k)

    def _first_call_(self, routine, args):
        from obin.objects.object_space import newvector
        self._receiver_ = routine

        self._yield_ = W_CoroutineYield(self)
        self._yield_.set_receiver(self._receiver_)

        if args is not None:
            args.prepend(self._yield_)
        else:
            args = newvector([self._yield_])

        self._routine_ = self.function().create_routine(args)
        routine.process.call_routine(self._routine_, self._receiver_, self._receiver_)

    def _iterator_(self):
        return W_CoroutineIterator(self)

    def _call_(self, routine, args):
        from obin.objects.object_space import newundefined
        assert routine

        if not self._routine_:
            return self._first_call_(routine, args)

        if not self._routine_.is_suspended():
            raise ObinRuntimeError(u"Invalid coroutine state")

        # TODO THIS IS TOTALLY WRONG, CHANGE IT TO PATTERN MATCH
        if args is not None:
            value = args.at(0)
        else:
            value = newundefined()

        receiver = routine
        self._yield_.set_receiver(receiver)
        routine.process.yield_to_routine(self._receiver_, receiver, value)
