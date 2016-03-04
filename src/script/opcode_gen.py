UNKNOW_CHANGE = -128

OPCODES = [
    ("VOID", 1),
    ("TRUE", 1),
    ("FALSE", 1),
    ("LITERAL", 1),
    ("SYMBOL", 1),
    ("OUTER", 1),
    ("LOCAL", 1),
    ("IMPORTED", 1),
    ("FUNCTION", 1),
    ("INTEGER", 1),
    ("DUP", 1),
    ("NEXT", 1),
    ("MODULE", 1),
    ("GENERIC", 1),
    ("ARGUMENTS", 1),
    ("FSELF", 1),
    ("FENV", 1),

    ("TRAIT", 0),

    ("LABEL", 0),
    ("STORE_LOCAL", 0),
    ("ITERATOR", 0),
    ("RETURN", 0),
    ("POP_CATCH", 0),

    ("CALL", 0),
    
    ("JUMP", 0),
    ("JUMP_IF_FALSE_NOPOP", 0),
    ("JUMP_IF_TRUE_NOPOP", 0),
    ("JUMP_IF_FALSE", 0),
    ("JUMP_IF_TRUE", 0),
    ("PUSH_CATCH", 0),
    ("JUMP_IF_ITERATOR_EMPTY", -1),

    ("METHOD", -1),
    ("MEMBER_DOT", -1),
    ("MEMBER", -1),
    ("POP", -1),
    ("THROW", -1),
    ("TYPE", -1),
    ("UNION", -1),

    ("STORE_MEMBER", -2),
    ("SLICE", -3),
    ("IMPLEMENT", -2),

    ("UNPACK_SEQUENCE", "__UNKNOWN_CHANGE__"),
    ("VECTOR", "__UNKNOWN_CHANGE__"),
    ("TUPLE", "__UNKNOWN_CHANGE__"),
    ("MAP", "__UNKNOWN_CHANGE__"),
    ("LIST", "__UNKNOWN_CHANGE__"),
    ("SPECIFY", "__UNKNOWN_CHANGE__"),
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
    S = "__UNKNOWN_CHANGE__ = %d\n\n" % UNKNOW_CHANGE
    S += "__STACK_CHANGES__ = ["
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