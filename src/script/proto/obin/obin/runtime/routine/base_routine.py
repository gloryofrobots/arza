class BaseRoutine:
    class State:
        IDLE = -1
        COMPLETE = 0
        INPROCESS = 2
        TERMINATED = 3
        SUSPENDED = 4

    def __init__(self):
        self.process = None
        self.__continuation = None
        self.__state = BaseRoutine.State.IDLE
        self.called = None
        self.result = None
        self.__signal = None

    def signal(self):
        return self.__signal

    def has_continuation(self):
        return self.__continuation is not None

    def set_continuation(self, continuation):
        # if continuation is self.__continuation:
        #     return

        if self.__continuation:
            print self, "\n**************\n", continuation

        assert not self.__continuation
        self.__continuation = continuation

    def continuation(self):
        return self.__continuation

    def resume(self, value):
        # print "RESUME", self.__state
        assert self.is_suspended()
        self._on_resume(value)
        self.called = None
        self.__state = BaseRoutine.State.INPROCESS

    def _on_resume(self, value):
        raise NotImplementedError()

    def inprocess(self):
        assert not self.is_closed()
        self.__state = BaseRoutine.State.INPROCESS

    def complete(self, result):
        assert not self.is_closed()
        self.result = result
        self.__state = BaseRoutine.State.COMPLETE
        self._on_complete()

    def _on_complete(self):
        raise NotImplementedError()

    def terminate(self, signal):
        assert not self.is_closed()
        assert signal is not None
        self.__signal = signal
        self.__state = BaseRoutine.State.TERMINATED
        self._on_terminate(signal)

    def _on_terminate(self, signal):
        raise NotImplementedError()

    def activate(self, process):
        assert not self.process
        self.process = process

        self._on_activate()
        self.inprocess()

    def _on_activate(self):
        pass

    def suspend(self):
        assert not self.is_closed()
        self.__state = BaseRoutine.State.SUSPENDED

    def execute(self):
        if self.is_complete():
            raise RuntimeError("Already complete")
        self._execute()

    def _execute(self):
        raise NotImplementedError()

    def is_inprocess(self):
        return self.__state == BaseRoutine.State.INPROCESS

    def is_idle(self):
        return self.__state == BaseRoutine.State.IDLE

    def is_complete(self):
        return self.__state == BaseRoutine.State.COMPLETE

    def is_terminated(self):
        return self.__state == BaseRoutine.State.TERMINATED

    def is_suspended(self):
        return self.__state == BaseRoutine.State.SUSPENDED

    def is_closed(self):
        return self.__state == BaseRoutine.State.COMPLETE \
               or self.__state == BaseRoutine.State.TERMINATED

    def call_routine(self, routine):
        assert self.process
        self.process.call_routine(routine, self, self)
