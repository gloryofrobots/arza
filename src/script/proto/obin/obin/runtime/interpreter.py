from rpython.rlib.streamio import open_file_as_stream
from obin.runtime.machine import Machine

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
        import obin.builtins.interpreter
        from obin.objects.datastructs import Slots

        self.machine = Machine()

        self.config = InterpreterConfig(config)
        self.global_object = newobject()
        self.modules = []

        self.symbols = Slots()
        object_space.global_object = self.global_object
        object_space.interpreter = self

        obin.builtins.setup_builtins(self.global_object)
        # obin.builtins.interpreter.setup_builtins(self.global_object)

    def load_module(self, filename):

        pass

    def run_src(self, src):
        from obin.compile.compiler import compile as cl
        code = cl(src)
        return self.run(code)

    # run_src = run_src_old

    def run(self, code, interactive=False):
        from obin.runtime.routine import GlobalRoutine

        print [str(c) for c in code.opcodes]
        global_routine = GlobalRoutine(code)

        print "*********"
        for c in [str(c) for c in code.compiled_opcodes]: print c
        print "*********"
        
        from obin.objects.object_space import object_space
        from obin.runtime.execution_context import ObjectExecutionContext

        ctx = ObjectExecutionContext(global_routine, self.global_object)
        object_space.global_context = ctx
        global_routine.set_context(ctx)

        result = self.machine.run_with(global_routine)
        print result
        return result
