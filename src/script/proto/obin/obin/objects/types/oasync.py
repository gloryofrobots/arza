from oroot import W_Root, W_Callable
from obin.runtime.exception import *
from obin.objects import api
from rpython.rlib import jit

class W_CoroutineIterator(W_Root):
    def __init__(self,  coroutine):
        self._coroutine_ = coroutine

    def _tobool_(self):
        return self._coroutine_.is_accessible()

    def _next_(self):
        from obin.objects.space import newinterrupt
        self._coroutine_._call_(self._coroutine_.process.routine, None)
        return newinterrupt()

    def _tostring_(self):
        return "CoroutineIterator"


class W_CoroutineYield(W_Callable):
    def __init__(self, coroutine):
        self.co = coroutine
        self.fiber = None

    def _tostring_(self):
        return "fn coroutine.yield {[native code]}"

    def _tobool_(self):
        return True

    def _call_(self, process, args):
        assert self.fiber

        if not self.co.is_accessible():
            raise ObinRuntimeError(u"Can not yield from coroutine")

        # self.co.fiber = process.fiber

        # TODO THIS IS WRONG
        value = api.at_index(args, 0)
        process.switch_to_fiber(self.fiber, value)


class W_Coroutine(W_Callable):
    # _immutable_fields_ = ['_function_']

    def __init__(self, function):
        self.function = function
        self.routine = None
        self.fiber = None
        self.yielder = W_CoroutineYield(self)

    def is_accessible(self):
        return self.routine is None or not self.routine.is_closed()

    def set_receiver(self, co):
        self.receiver = co

    def _tostring_(self):
        return "fn coroutine {[native code]}"

    def _tobool_(self):
        return True

    def _lookup_(self, k):
        from obin.objects.space import stdlib
        return api.at(stdlib.traits.Coroutine, k)

    def _first_call_(self, process, args):
        from obin.objects.space import newvector

        self.yielder.fiber = process.fiber

        if args is None:
            args = newvector([self.yielder])
        else:
            args.prepend(self.yielder)

        self.fiber = process.spawn_fiber(self.function, args)

    def _iterator_(self):
        return W_CoroutineIterator(self)

    def _call_(self, process, args):
        from obin.objects.space import newundefined

        if not self.fiber:
            return self._first_call_(process, args)

        if not self.fiber.is_waiting():
            raise ObinRuntimeError(u"Invalid coroutine state")

        # TODO THIS IS TOTALLY WRONG, CHANGE IT TO PATTERN MATCH
        if args is not None:
            value = api.at_index(args, 0)
        else:
            value = newundefined()

        process.switch_to_fiber(self.fiber, value)
