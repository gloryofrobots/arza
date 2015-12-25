class Fiber:
    def __init__(self, routine):
        self.routines = [routine]
        self.current = routine
        self.destination = None


class Process(object):
    class State:
        IDLE = 1
        ACTIVE = 2
        SUSPENDED = 3
        TERMINATED = 4

    def __init__(self, builtins):
        from obin.runtime.primitives import newprimitives
        self.__state = Process.State.IDLE

        self.fibers = []
        self.__fiber = None
        self.result = None
        self.__primitives = newprimitives()
        self.builtins = builtins
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
        return self.fiber().current

    @property
    def fiber(self):
        return self.__fiber

    @fiber.setter
    def fiber(self, f):
        self.__fiber = f

    def create_fiber(self, routine):
        f = Fiber(routine)
        f.destination = self.__fiber
        return f

    def purge_fiber(self, fiber):
        assert len(fiber.routines) == 0
        assert not fiber.current
        self.fibers.remove(fiber)

    def call_object(self, obj, args):
        routine = obj.create_routine(args)
        self.call_routine(routine)

    def resume_fiber(self, fiber1, fiber2, result):
        fiber2.current.suspend()
        fiber1.current.resume(result)
        self.fiber = fiber1

    def call_routine(self, routine):
        fiber = self.fiber
        assert routine is not fiber.current
        fiber.current.suspend()
        fiber.routines.append(fiber.current)
        fiber.current = routine
        routine.activate()

    def catch_signal(self):
        raise NotImplementedError("Throw in code")

    def evaluate_module(self, module):
        from obin.objects.types import omodule
        assert not self.fiber
        routine = omodule.compile_module(module, self.builtins)
        self.fiber = self.create_fiber(routine)
        routine.activate()
        self.run()
        module.result = self.result
        self.result = None
        # print "run_with_module", module.result()
        return module.result

    def run_module_force(self, module, _globals):
        raise NotImplementedError()
        # from obin.objects.types import omodule
        # routine = omodule.compile_module(module, _globals)
        # routine.activate(self)
        # routine.execute()

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

    def fiber_next(self, fiber):
        if len(fiber.routines) == 0:
            fiber.current = None
            return False

        routine = fiber.routines.pop()
        routine.resume(fiber.current.result)
        fiber.current = routine
        return routine

    def execute(self):
        # print "execute"
        fiber = self.fiber
        routine = self.fiber.current
        assert routine
        assert routine.is_inprocess()
        routine.execute(self)

        if routine.is_complete():
            result = routine.result
            if self.fiber_next(fiber) is False:
                destination = fiber.destination
                if not destination:
                    self.result = result
                    self.purge_fiber(self.fiber)
                    self.fiber = None
                    self.terminate()
                    return
                else:
                    self.resume_fiber(destination, self.fiber, result)

        elif routine.is_terminated():
            return self.catch_signal()

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

    # TODO THERE NO IS_COMPLETE HERE
    # PROCESS CAN BE EMPTY, TERMINATED AND ACTIVE
    def is_complete(self):
        if self.is_terminated():
            return True

        if self.fiber is None:
            return True

        if self.routine() is None:
            return True

        return False


    # def resume_routine(self, routine_to_resume, calling_routine, value):
    #     assert self.routine is calling_routine
    #     assert routine_to_resume.is_suspended()
    #     assert calling_routine.is_inprocess()
    #
    #     # check_continuation_consistency(routine_to_resume, routine_resume_from)
    #     calling_routine.suspend()
    #     calling_routine.called = routine_to_resume
    #     routine_to_resume.resume(value)
    #     self.set_active_routine(routine_to_resume)
