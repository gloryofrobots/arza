from obin.objects import api

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

        self.__idle()

    """
    PUBLIC API
    """

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

    def is_terminated(self):
        return self.state == Process.State.TERMINATED

    def is_active(self):
        return self.state == Process.State.ACTIVE

    def is_idle(self):
        return self.state == Process.State.IDLE

    def call_object(self, obj, args):
        from obin.objects import api
        routine = api.to_routine(obj, args)
        self.fiber.call(routine)

    def run(self, func, args):
        from obin.objects import api
        assert self.is_idle()
        assert not self.fiber

        routine = api.to_routine(func, args)
        self.fiber = self.__new_fiber(routine)
        return self.__run()

    def subprocess(self, func, args):
        child = Process(self.__data)
        result = child.run(func, args)
        return result

    def spawn_fiber(self, func, args):
        routine = api.to_routine(func, args)
        assert self.fiber
        self.fiber.stop_routine()
        f = self.__new_fiber(routine)
        self.fiber = f
        return f

    def switch_to_fiber(self, fiber, result):
        assert fiber is not self.fiber
        assert self.fiber.is_working()

        assert fiber.routine.is_suspended()

        self.fiber.stop_routine()
        fiber.resume_routine(result)
        self.fiber = fiber


    """
    PRIVATE API
    """

    def __catch_signal(self):
        raise NotImplementedError("Throw in code")

    def __run(self):
        # print "RUN"
        assert self.is_idle()
        self.__active()
        result = None
        while True:
            if not self.is_active():
                break
            try:
                result = self.__execute()
            except Exception:
                self.__terminate()
                raise

        assert len(self.fibers) == 0
        assert self.fiber is None
        self.__idle()
        return result

    def __new_fiber(self, routine):
        assert routine.is_idle()
        f = Fiber(routine, self.__fiber)
        self.fibers.append(f)
        routine.activate()
        return f

    def __purge_fiber(self, fiber):
        assert fiber.is_finished()
        self.fibers.remove(fiber)

    def __execute(self):
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
            self.__purge_fiber(fiber)
            if not parent_fiber:
                self.__terminate()
                return routine.result
            else:
                self.fiber = parent_fiber
                return None

        elif routine.is_terminated():
            self.__catch_signal()

        # if suspended reach here
        return None

    def __set_state(self, s):
        self.__state = s

    def __terminate(self):
        # print "F terminate"
        self.fiber = None
        self.fibers = []
        self.__set_state(Process.State.TERMINATED)

    def __active(self):
        # print "F activate"
        self.__set_state(Process.State.ACTIVE)

    def __idle(self):
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
