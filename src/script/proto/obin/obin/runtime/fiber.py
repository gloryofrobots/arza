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
            return

        self.__routine = r

    def execute(self):
        self.find_routine_to_execute()
        if self.routine() is None:
            self.terminate()
            return
        self.routine().execute()

    def find_routine_to_execute(self):
        routine = self.__routine
        while True:
            if routine is not None and routine.is_complete() is True:
                routine = routine.caller()
                break

        self.__routine = routine

    def is_terminated(self):
        return self.__state == Fiber.State.TERMINATED

    def terminate(self):
        self.__state = Fiber.State.TERMINATED

    def is_suspended(self):
        return self.__state == Fiber.State.SUSPENDED

    def suspend(self):
        self.__state = Fiber.State.SUSPENDED

    def is_active(self):
        return self.__state == Fiber.State.ACTIVE

    def activate(self):
        self.__state = Fiber.State.ACTIVE

    def is_idle(self):
        return self.__state == Fiber.State.IDLE

    def is_complete(self):
        if self.__routine is None:
            return False
        if self.__routine.is_complete() and self.__routine.has_caller() is False:
            return True

        return False

    def result(self):
        if not self.is_complete():
            return None

        return self.routine().result()
