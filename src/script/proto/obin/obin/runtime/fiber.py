__author__ = 'gloryofrobots'

def check_continuation_consistency(caller, continuation):
    r = continuation
    while True:
        if r is caller:
            break

        if not r:
            raise RuntimeError("Continuation not consistent. Continuation chain is empty")

        r = r.continuation()

class Fiber(object):
    class State:
        IDLE = 1
        ACTIVE = 2
        SUSPENDED = 3
        TERMINATED = 4

    def __init__(self):
        self.__state = Fiber.State.IDLE
        self.__routine = None
        self.result = None

    def state(self):
        return self.__state

    def __set_state(self, s):
        self.__state = s

    def routine(self):
        return self.__routine

    def call_object(self, obj, ctx, args):
        routine = obj.create_routine(ctx, args)
        self.call_routine(routine, ctx.routine(), ctx.routine())

    def call_routine(self, routine, continuation, caller):
        assert caller == self.routine()
        check_continuation_consistency(caller, continuation)

        self.__call_routine(routine, continuation, caller)

    def __call_routine(self, routine, continuation, caller):
        if caller:
            assert not caller.is_closed()
            assert not continuation.is_closed()

            if caller.called is not None:
                raise RuntimeError("Called has exists")

            caller.called = routine
            caller.suspend()

        if continuation:
            routine.set_continuation(continuation)

        routine.activate(self)
        self.set_active_routine(routine)

    def set_active_routine(self, r):
        if self.__routine is r:
            raise RuntimeError("Routine been already called")

        self.__routine = r

    def execute(self):
        self.find_routine_to_execute()

        if self.routine() is None:
            return

        self.routine().execute()

    def complete_last_routine(self, result):
        routine = self.__routine
        assert self.__routine.is_block()

        while True:
            if routine is None:
                raise RuntimeError("Routine for completion is absent")

            if routine.is_block():
                routine = routine.continuation()
                continue

            if not routine.is_suspended():
                raise RuntimeError("Routine in call stack not suspended")

            self.__routine = routine
            self.__routine.complete(result)

    def find_routine_to_execute(self):
        routine = self.__routine
        while True:
            if routine is None:
                break

            if routine.is_complete():
                continuation = routine.continuation()
                if not continuation:
                    self.result = routine.result
                    self.terminate()
                    routine = None
                    break

                # continuation can be suspended in case of normal call
                if continuation.is_suspended():
                    continuation.resume(routine.result)
                # and idle in ensured blocks and similar abnormal cases
                elif continuation.is_idle():
                    continuation.activate(self)
                    continuation.inprocess()

                routine = continuation
                continue
            break

        self.__routine = routine

        if routine is None:
            return

        if routine.is_terminated():
            return self.catch_signal()

    def catch_signal(self):
        routine = self.__routine
        assert routine.is_terminated()
        signal = routine.signal()
        assert signal

        while True:
            handler = routine.catch_signal(signal)
            if handler:
                from obin.runtime.context import CatchExecutionContext

                catch_ctx = CatchExecutionContext(handler, handler.signal_name(), signal, routine.ctx)
                handler.set_context(catch_ctx)
                routine = handler
                break
            else:
                if not routine.is_closed():
                    routine.terminate(signal)

            if routine.has_continuation():
                routine = routine.continuation()
                continue

            self.terminate()
            raise RuntimeError("NonHandled signal", signal)

        # continuation in signal handler must exists at this moment
        self.__call_routine(routine, None, None)

    def is_terminated(self):
        return self.__state == Fiber.State.TERMINATED

    def terminate(self):
        # print "F terminate"
        self.__state = Fiber.State.TERMINATED

    def is_suspended(self):
        return self.__state == Fiber.State.SUSPENDED

    def suspend(self):
        # print "F suspend"
        self.__state = Fiber.State.SUSPENDED

    def is_active(self):
        return self.__state == Fiber.State.ACTIVE

    def active(self):
        # print "F activate"
        self.__state = Fiber.State.ACTIVE

    def is_idle(self):
        return self.__state == Fiber.State.IDLE

    def is_complete(self):
        if self.is_terminated():
            return True
        if self.__routine is None:
            return True
        if self.__routine.is_complete() and self.__routine.has_continuation() is False:
            return True

        return False

