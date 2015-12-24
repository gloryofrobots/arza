
def run_routine_for_result(routine, ctx=None):
    if ctx:
        routine.set_context(ctx)
    m = Process()
    result = m.run_with(routine)
    return result


def run_function_for_result(function, args):
    routine = function.create_routine(args)
    m = Process()
    result = m.run_with(routine)
    return result


def check_continuation_consistency(caller, continuation):
    r = continuation
    while True:
        if r is caller:
            break

        if not r:
            raise RuntimeError("Continuation not consistent. Continuation chain is empty")

        r = r.continuation()


class Process(object):
    class State:
        IDLE = 1
        ACTIVE = 2
        SUSPENDED = 3
        TERMINATED = 4

    def __init__(self):
        from obin.runtime.primitives import newprimitives
        from obin.objects.space import newplainobject
        self.__state = Process.State.IDLE
        self.__routine = None
        self.result = None
        self.__primitives = newprimitives()
        self.builtins = newplainobject()
        self.modules = {}
        self.path = []

    def add_path(self, path):
        assert isinstance(path, str)
        self.path.append(path)

    def add_module(self, name, module):
        self.modules[name] = module

    def get_module(self, name):
        return self.modules[name]

    def get_primitive(self, pid):
        return self.__primitives[pid]

    @property
    def routine(self):
        return self.__routine

    def call_object(self, obj, calling_routine, args):
        routine = obj.create_routine(args)
        self.call_routine(routine, calling_routine, calling_routine)

    def yield_to_routine(self, routine_to_resume, routine_resume_from, value):
        assert self.routine is routine_resume_from
        assert routine_to_resume.is_suspended()
        assert routine_resume_from.is_inprocess()

        # check_continuation_consistency(routine_to_resume, routine_resume_from)
        routine_resume_from.suspend()
        routine_resume_from.called = routine_to_resume
        routine_to_resume.resume(value)
        self.set_active_routine(routine_to_resume)

    def call_routine(self, routine, continuation, caller):
        assert caller is self.routine
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
        # print "execute"
        self.find_routine_to_execute()
        # print "Process_routine", self.routine
        if self.routine is None:
            # print "Routine not here"
            return

        self.routine.execute()

    def find_routine_to_execute(self):
        routine = self.__routine
        # print "find_routine_to_execute", routine
        while True:
            if routine is None:
                # print "exit loop", routine
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

                routine = continuation
                continue
            break

        self.__routine = routine

        if routine is None:
            return None

        if routine.is_terminated():
            return self.catch_signal()

    def catch_signal(self):
        raise NotImplementedError()
        # routine = self.__routine
        # assert routine.is_terminated()
        # signal = routine.signal()
        # assert signal
        # while True:
        #     handler = routine.catch_signal(signal)
        #     if handler:
        #         assert 0
        #         # catch_ctx = CatchContext(handler, handler.signal_name(), signal, routine.ctx)
        #         # handler.set_context(catch_ctx)
        #         # routine = handler
        #         break
        #     else:
        #         if not routine.is_closed():
        #             routine.terminate(signal)
        #
        #     if routine.has_continuation():
        #         routine = routine.continuation()
        #         continue
        #
        #     self.terminate()
        #     raise RuntimeError("NonHandled signal", signal)
        #
        # # continuation in signal handler must exists at this moment
        # self.__call_routine(routine, None, None)

    def run_with_module(self, module, _globals):
        from obin.objects.types import omodule
        routine = omodule.compile_module(module, _globals)
        self.call_routine(routine, None, None)

        self.run()
        module.result = self.result
        self.result = None
        # print "run_with_module", module.result()
        return module.result

    def run_module_force(self, module, _globals):
        from obin.objects.types import omodule
        routine = omodule.compile_module(module, _globals)
        routine.activate(self)
        routine.execute()

    def run_with(self, routine):
        self.call_routine(routine, None, None)
        self.run()
        return self.result

    def run(self):
        # print "RUN"
        assert self.is_idle()
        self.active()
        while True:
            if not self.is_active():
                break
            try:
                self.execute()
            except Exception:
                self.terminate()
                raise

    def state(self):
        return self.__state

    def __set_state(self, s):
        self.__state = s

    def is_terminated(self):
        return self.state() == Process.State.TERMINATED

    def terminate(self):
        # print "F terminate"
        self.__set_state(Process.State.TERMINATED)

    def is_suspended(self):
        return self.state() == Process.State.SUSPENDED

    def suspend(self):
        # print "F suspend"
        self.__set_state(Process.State.SUSPENDED)

    def is_active(self):
        return self.state() == Process.State.ACTIVE

    def active(self):
        # print "F activate"
        self.__set_state(Process.State.ACTIVE)

    def is_idle(self):
        return self.state() == Process.State.IDLE

    def is_complete(self):
        if self.is_terminated():
            return True
        if self.__routine is None:
            return True
        if self.__routine.is_complete() and self.__routine.has_continuation() is False:
            return True

        return False
