from tpl import render
OPERATORS = [
    ("-", "negate", 'prefix'),
    # ("+", "__plus__", 'prefix'),
    # ("~", "~", 'prefix'),
    # ("not", "not", 'prefix'),


    # ("|", "|", 'infixr', 35),
    # ("^","^", 'infixr', 45),
    # ("&", "&", 'infixr', 45),

    ("<", "<", 'infixl', 50),
    (">", ">", 'infixl', 50),
    (">=", ">=", 'infixl', 50), 
    ("<=", "<=", 'infixl', 50),
    ("==", "==", 'infixl', 50),
    ("!=", "!=", 'infixl', 50), 

    # ("<<","<<", 'infixl', 55),
    # (">>",">>", 'infixl', 55),
    # (">>>", ">>>", 'infixl', 55),

    ("+","+", 'infixl', 60), 
    ("-", "-", 'infixl', 60),

    ("%", "%", 'infixl', 65), 
    ("*", "*", 'infixl', 65),
    ("/", "/", 'infixl', 65),

    ("::", "::", 'infixr', 70),
    ("++", "++", 'infixl', 70),

]

def symbol(name):
    return "%s" % name


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
            print '@%s %s %s' % (arityname, symbol(operator), symbol(name))
        else:
            precedence = op[3]
            if precedence:
                print '@%s %s %s %d' % (arityname, symbol(operator), symbol(name), precedence)

def gen_pairs():
    for op in OPERATORS:
        operator = op[0]
        name = op[1]
        arityname = op[2]
        print '"%s":"%s",' % (operator, name)




# gen_declarations()
gen_pairs()
