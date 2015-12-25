from oroot import W_Root
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
        value = api.at_index(args, 0)
        routine.process.resume_routine(self._receiver_, routine, value)


class W_Coroutine(W_Root):
    # _immutable_fields_ = ['_function_']

    def __init__(self, function, process):
        self.function = function
        self.routine = None
        self.receiver = None
        self.yielder = None
        self.process = process

    def is_accessible(self):
        return self.routine is None or not self.routine.is_closed()

    def set_receiver(self, co):
        self.receiver = co

    def _tostring_(self):
        return "fn coroutine {[native code]}"

    def _tobool_(self):
        return True

    def _lookup_(self, k):
        from obin.objects.space import state
        return api.at(state.traits.Coroutine, k)

    def _first_call_(self, routine, args):
        from obin.objects.space import newvector
        self.receiver = routine

        self.yielder = W_CoroutineYield(self)
        self.yielder.set_receiver(self.receiver)

        if args is None:
            args = newvector([self.yielder])
        else:
            args.prepend(self.yielder)

        self.routine = self.function.create_routine(args)
        routine.process.call_routine(self.routine, self.receiver, self.receiver)

    def _iterator_(self):
        return W_CoroutineIterator(self)

    def _call_(self, routine, args):
        from obin.objects.space import newundefined
        assert routine

        if not self.routine:
            return self._first_call_(routine, args)

        if not self.routine.is_suspended():
            raise ObinRuntimeError(u"Invalid coroutine state")

        # TODO THIS IS TOTALLY WRONG, CHANGE IT TO PATTERN MATCH
        if args is not None:
            value = api.at_index(args, 0)
        else:
            value = newundefined()

        receiver = routine
        self.yielder.set_receiver(receiver)
        routine.process.resume_routine(self.receiver, receiver, value)
