__author__ = 'gloryofrobots'


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

    def call_routine(self, routine):
        routine.call_from_fiber(self)
        self.set_active_routine(routine)

    """
    public void callExecutable(STExecutableObject executable) {
        Routine routine = executable.createRoutine();
        routine.call(this);
    }
    """
    def set_active_routine(self, r):
        if self.__routine is r:
            raise RuntimeError("Routine been already called")

        self.__routine = r

    def execute(self):
        self.find_routine_to_execute()

        if self.routine() is None:
            return

        self.routine().execute()

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

                continuation.resume(routine.result)
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
                routine = handler
                break

            if routine.has_continuation():
                routine = routine.continuation()
                continue

            self.terminate()
            raise RuntimeError("NonHandled signal", signal)

        self.__routine = routine

    def is_terminated(self):
        return self.__state == Fiber.State.TERMINATED

    def terminate(self):
        print "F terminate"
        self.__state = Fiber.State.TERMINATED

    def is_suspended(self):
        return self.__state == Fiber.State.SUSPENDED

    def suspend(self):
        print "F suspend"
        self.__state = Fiber.State.SUSPENDED

    def is_active(self):
        return self.__state == Fiber.State.ACTIVE

    def activate(self):
        print "F activate"
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

