def initialize(libdirs):
    from obin.builtins import setup_builtins
    from obin.runtime.process import Process, ProcessData, Modules
    from obin.objects.space import newplainobject, stdlib

    builtins = newplainobject()
    setup_builtins(builtins, stdlib)
    loader = Modules(libdirs)

    process = Process(ProcessData(loader, stdlib, builtins))
    return process

def evaluate_file(process, filename):
    from obin.utils import fs
    src = fs.load_file_content(filename)
    return evaluate(process, src)

def evaluate(process, src):
    from obin.runtime.load import compile_module
    from obin.objects.space import newstring
    module = compile_module(process, newstring(u"__main__"), src)
    # print "run_src", module
    result = process.evaluate_module(module)
    return result
