OPERATORS = [
    ("-", "uminus", 'prefix'),
    ("+", "uplus", 'prefix'),
    ("~", "bitnot", 'prefix'),
    ("not", "not", 'prefix'),


    ("|", "bitor", 'infixr', 35),
    ("^","bitxor", 'infixr', 45),
    ("&", "bitand", 'infixr', 45),

    ("<", "lt", 'infixl', 50),
    (">", "gt", 'infixl', 50),
    (">=", "ge", 'infixl', 50), 
    ("<=", "le", 'infixl', 50),
    ("==", "eq", 'infixl', 50),
    ("!=", "ne", 'infixl', 50), 

    ("notin", "notin", 'infixl', 50),
    ("nota", "nota", 'infixl', 50),
    ("isa", "isa", 'infixl', 50),
    ("kindof", "kindof", 'infixl', 50),
    ("is", "is", 'infixl', 50),   
    ("isnot","isnot", 'infixl', 50),
    ("in","in", 'infixl', 50), 

    ("<<","lsh", 'infixl', 55),
    (">>","rsh", 'infixl', 55),
    (">>>", "ursh", 'infixl', 55),

    ("+","add", 'infixl', 60), 
    ("-", "sub", 'infixl', 60),

    ("%", "mod", 'infixl', 65), 
    ("*", "mul", 'infixl', 65),
    ("\\", "div", 'infixl', 65),

    ("::", "cons", 'infixr', 70),

]


def operator_func_name(prim):
    return '___%s' % prim 

def op_name_var(name):
   return "OP_%s" %  name.upper()

def gen_names():
    for op in OPERATORS:
        name = op[1]
        print "%s = u\"%s\"" % (op_name_var(name), operator_func_name(name))

def gen_declarations():
    import re
    op_test = re.compile('\W')
    for op in OPERATORS:
        operator = op[0]
        name = op[1]
        arityname = op[2]
        if not op_test.match(operator):
            continue
        if arityname == 'prefix':
            print '@%s(%s, %s)' % (arityname, operator, operator_func_name(name))
        else:
            precedence = op[3]
            if precedence:
                print '@%s(%s, %s, %d)' % (arityname, operator, operator_func_name(name), precedence)


def gen_setup():
    TPL_SETUP = "    api.put_native_function(process, module, operators.%s, %s, %d)"
    for op in OPERATORS:
        operator = op[0],
        name = op[1]
        arityname = op[2]
        arity = 1 if arityname == 'prefix' else 2
        print TPL_SETUP % (op_name_var(name), operator_func_name(name), arity )

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
    for op in OPERATORS:
        operator = op[0],
        name = op[1]
        arityname = op[2]
        tpl = TPL_IMPL_UNARY if arityname == "prefix" else TPL_IMPL_BINARY

        print tpl % (operator_func_name(name),)


gen_names()
gen_setup()
gen_defs()
gen_declarations()
