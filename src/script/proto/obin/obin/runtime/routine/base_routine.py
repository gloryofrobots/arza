class BaseRoutine:
    class State:
        IDLE = -1
        COMPLETE = 0
        INPROCESS = 2
        TERMINATED = 3
        SUSPENDED = 4

    def __init__(self):
        self._state = BaseRoutine.State.IDLE
        self.result = None
        self._signal = None

    def signal(self):
        return self._signal

    def resume(self, value):
        # print "RESUME", self.__state
        if not self.is_suspended():
            print "SSS"
        assert self.is_suspended()
        self._on_resume(value)
        self._state = BaseRoutine.State.INPROCESS

    def _on_resume(self, value):
        raise NotImplementedError()

    def inprocess(self):
        assert not self.is_closed()
        self._state = BaseRoutine.State.INPROCESS

    def complete(self, result):
        assert not self.is_closed()
        self.result = result
        self._state = BaseRoutine.State.COMPLETE
        self._on_complete()

    def _on_complete(self):
        raise NotImplementedError()

    def terminate(self, signal):
        assert not self.is_closed()
        assert signal is not None
        self._signal = signal
        self._state = BaseRoutine.State.TERMINATED
        self._on_terminate(signal)

    def _on_terminate(self, signal):
        raise NotImplementedError()

    def activate(self):
        self.inprocess()

    def _on_activate(self):
        pass

    def suspend(self):
        assert not self.is_closed()
        self._state = BaseRoutine.State.SUSPENDED

    def execute(self, process):
        if self.is_complete():
            raise RuntimeError("Already complete")
        self._execute(process)

    def _execute(self, process):
        raise NotImplementedError()

    def is_inprocess(self):
        return self._state == BaseRoutine.State.INPROCESS

    def is_idle(self):
        return self._state == BaseRoutine.State.IDLE

    def is_complete(self):
        return self._state == BaseRoutine.State.COMPLETE

    def is_terminated(self):
        return self._state == BaseRoutine.State.TERMINATED

    def is_suspended(self):
        return self._state == BaseRoutine.State.SUSPENDED

    def is_closed(self):
        return self._state == BaseRoutine.State.COMPLETE \
               or self._state == BaseRoutine.State.TERMINATED

