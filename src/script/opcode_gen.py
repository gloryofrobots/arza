OPCODES = [
    ("LOAD_UNDEFINED", 1),
    ("LOAD_NULL", 1),
    ("LOAD_TRUE", 1),
    ("LOAD_FALSE", 1),
    ("LOAD_LITERAL", 1),
    ("LOAD_OUTER", 1),
    ("LOAD_LOCAL", 1),
    ("LOAD_FUNCTION", 1),
    ("LOAD_INTEGER", 1),
    ("DUP", 1),
    ("NEXT_ITERATOR", 1),

    ("LABEL", 0),
    ("STORE_OUTER", 0),
    ("STORE_LOCAL", 0),
    ("LOAD_ITERATOR", 0),
    ("RETURN", 0),

    ("CALL_PRIMITIVE", 0),
    ("CALL", 0),
    ("CALL_METHOD", 0),
    
    ("JUMP", 0),
    ("JUMP_IF_FALSE_NOPOP", 0),
    ("JUMP_IF_TRUE_NOPOP", 0),
    ("JUMP_IF_FALSE", 0),
    ("JUMP_IF_TRUE", 0),
    ("JUMP_IF_ITERATOR_EMPTY", -1),

    ("LOAD_MEMBER_DOT", -1),
    ("LOAD_MEMBER", -1),
    ("POP", -1),
    ("THROW", -1),
    ("CONCAT", -1),

    ("STORE_MEMBER", -2),

    ("PUSH_MANY", None),
    ("LOAD_VECTOR", None),
    ("LOAD_OBJECT", None),
]

def gen_ocode_ids():
    for i,op in enumerate(OPCODES):
        print "%s = %d" % (op[0], i)

def gen_opcode_repr():
    S = "__OPCODE_REPR__ = ["
    for p in OPCODES:
        S += "%s, " % str(("\"%s\"" % p[0]))

    S += "]"
    print S

def gen_opcode_stack_change():
    S = "__STACK_CHANGES__ = ["
    for p in OPCODES:
        S += "%s, " % str(p[1])

    S += "]"
    print S

def gen_opcode_to_str():
    print "def opcode_to_str(p):"
    print "    return __OPCODE_REPR__[p]\n\n"

gen_ocode_ids()
print "\n# ************************************************\n"
gen_opcode_repr()
print "\n# ************************************************\n"
gen_opcode_stack_change()
print "\n# ************************************************\n"
gen_opcode_to_str()