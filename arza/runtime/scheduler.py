from arza.types import space, api
from arza.builtins import builtins
from arza.runtime.process import Process
from arza.runtime import process_data, error
from arza.runtime.load import import_module, evaluate_module_file
import random
MAX_ID = 4294967295

if api.DEBUG_MODE:
    PRELUDE_FILE = u"prelude_debug"
else:
    PRELUDE_FILE = u"prelude"

STD_MODULES = [u"std", u"tuple",
               u"lense", u"list",
               u"string", u"generics",
               u"seq", u"coro",
               u"map", ]


# STD_MODULES = []

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
        self.root = None
        self.processes = []
        self.new_processes = []

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

        self.processes.append(self.root)

    def run(self, filename):
        try:
            module = evaluate_module_file(self.root, space.newsymbol(self.root, u"__main__"), filename)
        except error.LalanSignal as e:
            return e.signal

        main = api.at(module, space.newsymbol(self.root, u"main"))
        self.loop(main)

    def loop(self, main_func):
        self.root.run_cold(main_func, space.newunit())
        while True:
            if len(self.processes) == 0:
                return
            self._loop()

    def _loop(self):
        cycles = 3
        if len(self.new_processes) > 0:
            self.processes += self.new_processes
            self.new_processes = []

        for process in self.processes:
            process.iterate(cycles)
            if not process.is_active():
                self.update_processes(process)
                break

    def update_processes(self, process):
        self.processes.remove(process)

    def spawn(self, func, args):
        process = self.root.spawn()
        process.id = random.randrange(0, MAX_ID)

        self.processes.append(process)
        process.run_cold(func, args)

    @property
    def result(self):
        print self.root.is_complete()
        return self.root.result
