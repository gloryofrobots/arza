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
        from obin.objects.datastructs import Slots

        self.process = Process()

        self.primitives = {}
        self.config = InterpreterConfig(config)
        self.global_object = newobject()
        self.modules = []

        self.symbols = Slots()
        object_space.global_object = self.global_object
        object_space.interpreter = self

        obin.builtins.setup_builtins(self.global_object)
        # obin.builtins.interpreter.setup_builtins(self.global_object)

    def add_primitive(self, primitive_id, func):
        self.primitives[primitive_id] = func

    def get_primitive(self, primitive_id):
        return self.primitives[primitive_id]

    def load_module(self, filename):

        pass

    def run_src(self, src):
        from obin.compile.compiler import compile_module
        from obin.objects.object_space import newstring
        module = compile_module(newstring(u"__main__"), src)
        return self.run_module(module)

    def run_module(self, module):
        result = self.process.run_with_module(module)
        print result
        return result