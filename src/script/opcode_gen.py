UNKNOW_CHANGE = -128

OPCODES = [
    ("UNDEFINED", 1),
    ("NULL", 1),
    ("TRUE", 1),
    ("FALSE", 1),
    ("LITERAL", 1),
    ("OUTER", 1),
    ("LOCAL", 1),
    ("FUNCTION", 1),
    ("ORIGIN", 1),
    ("INTEGER", 1),
    ("DUP", 1),
    ("NEXT", 1),
    ("IMPORT", 1),
    ("IMPORT_MEMBER", 1),
    ("GENERIC", 1),
    ("TRAIT", 1),

    ("LABEL", 0),
    ("STORE_OUTER", 0),
    ("STORE_LOCAL", 0),
    ("ITERATOR", 0),
    ("RETURN", 0),

    ("CALL_INTERNAL", 0),
    ("CALL", 0),
    ("CALL_METHOD", 0),
    
    ("JUMP", 0),
    ("JUMP_IF_FALSE_NOPOP", 0),
    ("JUMP_IF_TRUE_NOPOP", 0),
    ("JUMP_IF_FALSE", 0),
    ("JUMP_IF_TRUE", 0),
    ("JUMP_IF_ITERATOR_EMPTY", -1),

    ("MEMBER_DOT", -1),
    ("MEMBER", -1),
    ("POP", -1),
    ("THROW", -1),
    ("VECTOR_MERGE_INTO", -1),

    ("STORE_MEMBER", -2),
    ("SLICE", -3),

    ("UNPACK_SEQUENCE", "__UNKNOWN_CHANGE__"),
    ("PUSH_MANY", "__UNKNOWN_CHANGE__"),
    ("VECTOR", "__UNKNOWN_CHANGE__"),
    ("TUPLE", "__UNKNOWN_CHANGE__"),
    ("MAP", "__UNKNOWN_CHANGE__"),
    ("LIST", "__UNKNOWN_CHANGE__"),
    ("REIFY", "__UNKNOWN_CHANGE__"),
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