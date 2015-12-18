from rpython.rlib.streamio import open_file_as_stream

def load_file(filename):
    f = open_file_as_stream(str(filename))
    src = f.readall()
    return src

def run_src(process, src):
    from obin.runtime.load import compile_module
    from obin.objects.space import newstring
    module = compile_module(process, newstring(u"__main__"), src)
    return run_module(process, module)

def run_module(process, module):
    from obin.objects.space import state
    result = process.run_with_module(module, state.builtins)
    return result

def initialize():
    from obin.builtins import setup_builtins
    from obin.runtime.process import Process
    from obin.objects.space import state
    state.process = Process()
    setup_builtins(state.builtins)
    return state