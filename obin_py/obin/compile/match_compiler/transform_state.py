class TransformState:
    def __init__(self, compiler, code, node):
        self.compiler = compiler
        self.code = code
        self.node = node


def transform_error(state, node, message):
    from obin.compile.compiler import compile_error
    return compile_error(state.compiler, state.code, node, message)
