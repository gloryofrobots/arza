def initialize(libdirs):
    from obin.builtins import setup_builtins
    from obin.runtime.process import Process
    from obin.runtime import process_data

    from obin.types.space import newsymbol
    from obin.runtime.load import import_module
    proc_data = process_data.create(libdirs)

    process = Process(proc_data)

    prelude = import_module(process, newsymbol(process, u"obin"))
    process.builtins = prelude.env
    setup_builtins(process)

    return process

def evaluate_file(process, filename):
    from obin.utils import fs
    src = fs.load_file_content(filename)
    return evaluate_string(process, src)


def evaluate_string(process, src):
    from obin.compile.compiler import compile_module
    from obin.types.space import newsymbol
    module = compile_module(process, newsymbol(process, u"__main__"), src)
    result = process.run(module, None)
    return result
