from obin.types import space
from obin.compile.compiler import compile_module
from obin.utils import fs
from obin.builtins import setup_builtins
from obin.runtime.process import Process
from obin.runtime import process_data
from obin.runtime.load import import_module


def initialize(libdirs):
    proc_data = process_data.create(libdirs)

    process = Process(proc_data)
    prelude = import_module(process, space.newsymbol(process, u"obin"))
    process.builtins = prelude.env
    setup_builtins(process)

    return process


def evaluate_file(process, filename):
    from obin.builtins.setup_globals import compile_module

    module = process.run(space.newnativefunc(space.newsymbol(process, u"compile_module"), compile_module, 2),
                                space.newtuple([space.newstring_from_str(filename), space.newsymbol(process,u"__main__")]))
    if process.is_terminated():
        # error here
        return module
    return space.newtuple([space.newsymbol(process, u"ok"), module.result])
    # src = fs.load_file_content(filename)
    # sourcename = space.newsymbol_py_str(process, filename)
    # module = evaluate_module(process, , filename)
    # module = compile_module(process, space.newsymbol(process,u"__main__"), src, sourcename)
    # result = process.run(module, None)
    # return result


