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
    """Creates a js interpreter"""
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
        from obin.compile.compiler import compile as cl
        from obin.objects.object_space import newfunc, newstring
        # fn = newfunc(newstring(u"Global"), code, None)
        code = cl(src)
        return self.run(code)

    # run_src = run_src_old

    def run(self, code):
        from obin.runtime.routine import create_bytecode_routine

        # print [str(c) for c in code.opcodes]


        global_routine = create_bytecode_routine(code)

        print "*********"
        for i, c in enumerate([str(c) for c in code.compiled_opcodes]): print i,c
        print "*********"
        
        from obin.objects.object_space import object_space
        from obin.runtime.context import create_object_context

        ctx = create_object_context(global_routine, self.global_object)
        object_space.global_context = ctx

        result = self.process.run_with(global_routine)
        print result
        return result
