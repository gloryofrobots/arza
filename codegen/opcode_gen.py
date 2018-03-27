from tpl import render

UNKNOW_CHANGE = -128

OPCODES = [
    ("VOID", 1),
    ("NIL", 1),
    ("TRUE", 1),
    ("FALSE", 1),
    ("LITERAL", 1),
    ("OUTER", 1),
    ("LOCAL", 1),
    ("TEMPORARY", 1),
    ("IMPORT_NAME", 1),
    ("FUNCTION", 1),
    ("DUP", 1),
    ("LOOKUP", -1),

    ("FARGS", 1),
    ("FSELF", 1),

    ("LABEL", 0),
    ("STORE_LOCAL_CONST", 0),
    ("STORE_LOCAL_VAR", 0),
    ("STORE_TEMPORARY", 0),
    ("RETURN", 0),
    ("POP_CATCH", 0),

    ("CALL", 0),

    ("JUMP", 0),
    ("JUMP_IF_FALSE_NOPOP", 0),
    ("JUMP_IF_TRUE_NOPOP", 0),
    ("JUMP_IF_FALSE", 0),
    # PUSH CATCH MUST BE PLACED BETWEEN JUMPS BECAUSE OF SPECIAL CARE IN source.py
    ("PUSH_CATCH", 0),
    ("JUMP_IF_TRUE", 0),

    ("POP", -1),
    ("THROW", -1),

    ("UNPACK_TUPLE", "__UNKNOWN_CHANGE__"),
    ("VECTOR", "__UNKNOWN_CHANGE__"),
    ("TUPLE", "__UNKNOWN_CHANGE__"),
    ("MAP", "__UNKNOWN_CHANGE__"),
    ("LIST", "__UNKNOWN_CHANGE__"),
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