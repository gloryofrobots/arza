def initialize(libdirs):
    from obin.builtins import setup_builtins
    from obin.runtime.process import Process, ProcessData, Modules
    from obin.objects.space import newplainobject
    from obin.objects.stdlib import StdLib

    stdlib = StdLib()
    builtins = newplainobject()
    setup_builtins(builtins, stdlib)
    loader = Modules(libdirs)

    process = Process(ProcessData(loader, stdlib, builtins))
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
