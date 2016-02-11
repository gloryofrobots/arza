from obin.types import space, api
from obin.builtins import setup_builtins
from obin.runtime.process import Process
from obin.runtime import process_data
from obin.runtime.load import import_module, evaluate_module_file

def newprocess(libdirs):
    core_prelude = space.newemptyenv(space.newstring(u"__core__"))
    proc_data = process_data.create(libdirs, core_prelude)
    process = Process(proc_data)
    setup_builtins(process, core_prelude)
    return process

# TODO MOVE ALL OF IT TO PROCESS
def initialize(libdirs):
    process = newprocess(libdirs)
    prelude = import_module(process, space.newsymbol(process, u"obin"))
    if process.is_terminated():
        # error here
        return process, prelude
    process.modules.set_prelude(prelude)

    return process, None


def evaluate_file(process, filename):
    module_or_error = evaluate_module_file(process, space.newsymbol(process, u"__main__"), filename)

    if process.is_terminated():
        # error here
        return module_or_error

    main = api.at(module_or_error, space.newsymbol(process, u"main"))
    result = process.subprocess(main, space.newtuple([]))

    if process.is_terminated():
        # error here
        return result

    return space.newtuple([space.newsymbol(process, u"ok"), result])
