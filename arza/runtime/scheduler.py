from arza.types import space, api, pid, plist
from arza.builtins import builtins
from arza.runtime.process import Process
from arza.runtime import process_data, error
from arza.runtime.load import import_module, evaluate_module_file
import random

if api.DEBUG_MODE:
    PRELUDE_FILE = u"prelude_debug"
else:
    PRELUDE_FILE = u"prelude"

STD_MODULES = [u"std", u"tuple",
               u"lense", u"list",
               u"string", u"generics",
               u"seq", u"coro",
               u"map",
               ]


def load_prelude(process, script_name):
    result = import_module(process, space.newsymbol(process, script_name))
    if process.is_terminated():
        # error here
        return result

    process.modules.set_prelude(result)
    return None


def load_module(process, script_name):
    result = import_module(process, space.newsymbol(process, script_name))
    if process.is_terminated():
        # error here
        return result
    return None


class Scheduler:
    def __init__(self):
        self.count = 0
        self.root = None
        self.active = plist.empty()
        # self.new = plist.empty()
        self.waiting = plist.empty()

    def create_root(self, libdirs):
        core_prelude = space.newemptyenv(space.newstring(u"prelude"))
        proc_data = process_data.create(self, libdirs, core_prelude)
        process = Process(proc_data)
        builtins.presetup(process, core_prelude, process.std)
        return process

    def _initialize_root(self, libdirs):
        path = space.newlist([space.newstring_s(p) for p in libdirs])

        process = self.create_root(path)
        err = load_prelude(process, PRELUDE_FILE)
        if err is not None:
            return process, err

        # HERE ORDER IS IMPORTANT!!!!!
        process.std.postsetup(process)
        error.initialise(process)
        builtins.postsetup(process)

        for module_name in STD_MODULES:
            err = load_module(process, module_name)
            if err is not None:
                return process, err

        print "INITIALIZED"
        return process, None

    def start(self, libdirs):
        self.root, err = self._initialize_root(libdirs)
        if err is not None:
            return error

        self.__add_active(self.root)

    def __add_active(self, p):
        # print "aa", p
        self.active = plist.cons(p, self.active)

    def __add_waiting(self, p):
        self.waiting = plist.cons(p, self.waiting)

    def run(self, filename):
        try:
            module = evaluate_module_file(self.root, space.newsymbol(self.root, u"__main__"), filename)
        except error.LalanSignal as e:
            return e.signal

        main = api.at(module, space.newsymbol(self.root, u"main"))
        self.loop(main)

    def loop(self, main_func):
        self.root.activate(main_func, space.newunit())
        while True:
            if self.is_unactive():
                return

            self._loop(self.active)

    def _loop(self, proceses):
        cycles = 3
        for p in proceses:
            if p.is_active():
                p.iterate(cycles)

    def is_unactive(self):
        return plist.is_empty(self.active)

    def unactivate(self, p):
        if self.is_unactive():
            return

        # print "unactivate", p
        self.active = plist.remove(self.active, p)

    def activate(self, p):
        self.__add_active(p)

    def wait(self, p):
        self.unactivate(p)
        self.__add_waiting(p)

    def wakeup(self, process):
        assert process in self.waiting
        self.waiting = plist.remove(self.waiting, process)
        self.__add_active(process)
        # print "wakeup", len(self.active)

    def spawn(self, func, args):
        process = self.root.spawn()
        self.count += 1
        id = self.count
        process.set_id(id)
        self.activate(process)
        process.activate(func, args)
        return pid.newpid(process)

    @property
    def result(self):
        return self.root.result
