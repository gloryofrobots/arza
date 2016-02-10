OPERATORS = [
    ("is", "is", 2), ("!=", "ne", 2), ("==", "eq", 2), ("not", "not", 1), ("isnot","isnot", 2),
    ("in","in", 2), ("+","add", 2), ("%", "mod", 2), ("*", "mul", 2),
    ("\\", "div", 2), ("-", "sub", 2), ("-", "uminus", 1),
    ("+", "uplus", 1), (">=", "ge", 2), (">", "gt", 2), ("<", "lt", 2),
    ("<=", "le", 2), ("~", "bitnot", 1), ("|", "bitor", 2), ("^","bitxor", 2),
    ("&", "bitand", 2), ("<<","lsh", 2), (">>","rsh", 2),
    (">>>", "ursh", 2), ("::", "cons", 2), ("notin", "notin", 2),
    ("nota", "nota", 2), ("isa", "isa", 2), ("kindof", "kindof", 2),
]

def operator_func_name(prim):
    return '___%s' % prim 


def gen_setup():
    TPL_SETUP = "    api.put_native_function(process, module, u\"%s\", %s, %d)"
    for operator, name, arity in OPERATORS:
        print TPL_SETUP % (operator_func_name(name), operator_func_name(name), arity )

def gen_defs():
    TPL_IMPL_UNARY = """
@complete_native_routine
def %s(process, routine):
    left = routine.get_arg(0)
    """

    TPL_IMPL_BINARY = """
@complete_native_routine
def %s(process, routine):
    left = routine.get_arg(0)
    right = routine.get_arg(1)
"""
    for operator, name, arity in OPERATORS:
        tpl = TPL_IMPL_UNARY if arity == 1 else TPL_IMPL_BINARY

        print tpl % (operator_func_name(name),)
gen_setup()
gen_defs()
