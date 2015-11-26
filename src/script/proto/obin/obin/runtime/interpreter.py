from rpython.rlib.streamio import open_file_as_stream
from obin.runtime.process import Process

def load_file(filename):
    f = open_file_as_stream(str(filename))
    src = f.readall()
    return src


class InterpreterConfig(object):
    def __init__(self, config={}):
        self.debug = config.get('debug', False)


class Interpreter(object):
    def __init__(self, config={}):
        from obin.objects.object_space import object_space, newobject
        import obin.builtins.interpreter_builtins

        self.process = Process()
        self.config = InterpreterConfig(config)
        self.builtins = newobject()
        self.modules = []
        object_space.interpreter = self

        obin.builtins.setup_builtins(self.builtins)

    def run_src(self, src):
        from obin.compile.compiler import compile_module
        from obin.objects.object_space import newstring
        module = compile_module(newstring(u"__main__"), src)
        return self.run_module(module)

    def run_module(self, module):
        result = self.process.run_with_module(module, self.builtins)
        return result
