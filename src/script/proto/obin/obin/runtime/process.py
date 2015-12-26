class Modules:
    def __init__(self, path):
        assert isinstance(path, list)
        self.modules = {}
        self.path = path

    def add_path(self, path):
        assert isinstance(path, str)
        self.path.append(path)

    def add_module(self, name, module):
        self.modules[name] = module

    def get_module(self, name):
        return self.modules[name]


class ProcessData:
    def __init__(self, modules, stdlib, builtins):
        self.modules = modules
        self.stdlib = stdlib
        self.builtins = builtins


class Fiber:
    def __init__(self, r, parent):
        assert r.is_idle()
        self.routines = []
        self.routine = r
        self.parent = parent

    def is_finished(self):
        assert len(self.routines) == 0
        return self.routine.is_closed()

    def is_working(self):
        return self.routine.is_inprocess()

    def is_waiting(self):
        return self.routine.is_suspended()

    def stop_routine(self):
        self.routine.suspend()

    def resume_routine(self, result):
        self.routine.resume(result)

    def finalise(self):
        parent = self.parent
        if parent is None:
            return None

        assert parent.routine.is_suspended()
        parent.routine.resume(self.routine.result)
        return parent

    def call(self, routine):
        assert routine is not self.routine
        self.routine.suspend()
        self.routines.append(self.routine)
        self.routine = routine
        routine.activate()

    def next_routine(self):
        if len(self.routines) == 0:
            return None

        routine = self.routines.pop()
        routine.resume(self.routine.result)
        self.routine = routine
        return routine


class Process(object):
    class State:
        IDLE = 1
        ACTIVE = 2
        TERMINATED = 4

    def __init__(self, data):
        assert isinstance(data, ProcessData)
        self.__data = data
        self.__state = None
        self.fibers = []
        self.__fiber = None

        self.idle()

    @property
    def modules(self):
        return self.__data.modules

    @property
    def stdlib(self):
        return self.__data.stdlib

    @property
    def builtins(self):
        return self.__data.builtins

    @property
    def fiber(self):
        return self.__fiber

    @fiber.setter
    def fiber(self, f):
        self.__fiber = f

    @property
    def state(self):
        return self.__state

    def __set_state(self, s):
        self.__state = s

    def call_object(self, obj, args):
        routine = obj.create_routine(args)
        self.call_routine(routine)

    def catch_signal(self):
        raise NotImplementedError("Throw in code")

    def evaluate_module(self, module):
        from obin.objects.types import omodule
        assert not self.fiber
        routine = omodule.compile_module(module)
        self.fiber = self._newfiber(routine)
        result = self.run()
        module.result = result
        # print "run_with_module", module.result()
        return result

    def run_module_force(self, module):
        from obin.objects.types import omodule
        routine = omodule.compile_module(module)
        routine.activate()
        routine.execute(self)

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
        assert len(self.fibers) == 0
        assert self.fiber is None
        self.idle()

    def _newfiber(self, routine):
        assert routine.is_idle()
        f = Fiber(routine, self.__fiber)
        self.fibers.append(f)
        routine.activate()
        return f

    def spawn_fiber(self, routine):
        assert self.fiber
        self.fiber.stop_routine()
        f = self._newfiber(routine)
        self.fiber = f
        return f

    def _purge_fiber(self, fiber):
        assert fiber.is_finished()
        self.fibers.remove(fiber)

    def switch_to(self, fiber, result):
        assert fiber is not self.fiber
        assert self.fiber.is_working()

        assert fiber.routine.is_suspended()

        self.fiber.stop_routine()
        fiber.resume_routine(result)
        self.fiber = fiber

    def call_routine(self, routine):
        self.fiber.call(routine)

    def execute(self):
        # print "execute"
        fiber = self.fiber
        routine = fiber.routine
        assert routine
        assert routine.is_inprocess()
        routine.execute(self)

        if routine.is_suspended():
            return None

        if routine.is_complete():
            continuation = fiber.next_routine()
            if continuation is not None:
                return None

            parent_fiber = fiber.finalise()
            self._purge_fiber(fiber)
            if not parent_fiber:
                self.terminate()
                return routine.result
            else:
                self.fiber = parent_fiber
                return None

        elif routine.is_terminated():
            self.catch_signal()

        # if suspended reach here
        return None

    def is_terminated(self):
        return self.state == Process.State.TERMINATED

    def terminate(self):
        # print "F terminate"
        self.fiber = None
        self.fibers = []
        self.__set_state(Process.State.TERMINATED)

    def is_active(self):
        return self.state == Process.State.ACTIVE

    def active(self):
        # print "F activate"
        self.__set_state(Process.State.ACTIVE)

    def is_idle(self):
        return self.state == Process.State.IDLE

    def idle(self):
        self.__set_state(Process.State.IDLE)


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
