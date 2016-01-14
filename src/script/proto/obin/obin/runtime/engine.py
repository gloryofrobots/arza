def initialize(libdirs):
    from obin.builtins import setup_builtins
    from obin.runtime.process import Process, ProcessState, Modules
    from obin.objects.space import newmap, newstring
    from obin.builtins.std import Std
    from obin.runtime.load import import_module
    stdlib = Std()
    builtins = newmap()
    loader = Modules(libdirs)
    process = Process(ProcessState(loader, stdlib, builtins))

    prelude = import_module(process, newstring(u"obin"))
    process.builtins = prelude.env
    setup_builtins(process, process.builtins, stdlib)

    return process


def evaluate_file(process, filename):
    from obin.utils import fs
    src = fs.load_file_content(filename)
    return evaluate_string(process, src)


def evaluate_string(process, src):
    from obin.compile.compiler import compile_module
    from obin.objects.space import newstring
    module = compile_module(process, newstring(u"__main__"), src)
    # print "run_src", module
    result = process.run(module, None)
    return result
