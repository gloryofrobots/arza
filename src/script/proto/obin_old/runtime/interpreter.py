from rpython.rlib.streamio import open_file_as_stream


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
        from obin.object.space import object_space
        from obin.object.obj import W_Object
        from obin import builtins
        from obin.builtins import interpreter

        self.config = InterpreterConfig(config)
        self.global_object = W_Object()

        object_space.global_object = self.global_object

        if object_space.interpreter is not None:
            raise RuntimeError("Only single Interpreter allowed")

        object_space.interpreter = self

        builtins.setup_builtins(self.global_object)
        interpreter.setup_builtins(self.global_object)

    def run_ast(self, ast):
        symbol_map = ast.symbol_map
        from obin.compile.code import ast_to_bytecode
        code = ast_to_bytecode(ast, symbol_map)
        return self.run(code)

    def run_src(self, src):
        from obin.compile.astbuilder import parse_to_ast
        from obin.runistr import decode_str_utf8
        ast = parse_to_ast(decode_str_utf8(src))
        return self.run_ast(ast)

    def run(self, code, interactive=False):
        from functions import JsGlobalCode

        from obin.compile.code import JsCode
        assert isinstance(code, JsCode)
        c = JsGlobalCode(code)

        from obin.compile.cjs.object_space import object_space
        from js.execution_context import GlobalExecutionContext

        ctx = GlobalExecutionContext(c, self.global_object)
        object_space.global_context = ctx

        result = c.run(ctx)
        return result.value
