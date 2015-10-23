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
        from obin.objects.object import W_ModuleObject
        from obin.objects.object_space import object_space
        import obin.builtins.interpreter
        from obin.objects.datastructs import Slots

        self.machine = Machine()

        self.config = InterpreterConfig(config)
        self.global_object = W_ModuleObject()
        self.modules = []

        self.symbols = Slots()
        object_space.global_object = self.global_object
        object_space.interpreter = self

        obin.builtins.setup_builtins(self.global_object)
        obin.builtins.interpreter.setup_builtins(self.global_object)

        object_space.assign_proto(self.global_object)

    def load_module(self, filename):

        pass

    def run_ast(self, ast):
        symbol_map = ast.symbol_map
        from obin.compile.code import ast_to_bytecode
        code = ast_to_bytecode(ast, symbol_map)
        #print code
        return self.run(code)

    def run_src(self, src):
        from obin.compile.astbuilder import parse_to_ast
        from obin.runistr import decode_str_utf8
        ast = parse_to_ast(decode_str_utf8(src))
        return self.run_ast(ast)

    def run(self, code, interactive=False):
        from obin.runtime.routine import GlobalRoutine

        from obin.compile.code import Code
        assert isinstance(code, Code)
        global_routine = GlobalRoutine(code)

        from obin.objects.object_space import object_space
        from obin.runtime.execution_context import ObjectExecutionContext

        ctx = ObjectExecutionContext(global_routine, self.global_object)
        object_space.global_context = ctx
        global_routine.set_context(ctx)

        result = self.machine.run_with(global_routine)
        print result
        return result
