OPCODES = [
    "LOAD_LIST",
    "NEXT_ITERATOR",
    "LOAD_MEMBER_DOT",
    "JUMP_IF_ITERATOR_EMPTY",
    "LOAD_LOCAL",
    "LABEL",
    "LOAD_OUTER",
    "LOAD_VECTOR",
    "STORE_MEMBER",
    "LOAD_MEMBER",
    "LOAD_OBJECT",
    "CALL",
    "LOAD_FUNCTION",
    "LOAD_ITERATOR",
    "CALL_METHOD",
    "JUMP_IF_FALSE_NOPOP",
    "JUMP_IF_TRUE_NOPOP",
    "JUMP_IF_FALSE",
    "DUP",
    "POP",
    "RETURN",
    "LOAD_NULL",
    "LOAD_UNDEFINED",
    "JUMP_IF_TRUE",
    "CALL_PRIMITIVE",
    "THROW",
    "LOAD_TRUE",
    "LOAD_FALSE",
    "LOAD_LITERAL",
    "JUMP",
    "STORE_OUTER",
    "STORE_LOCAL",
    "__LENGTH__",
]

def gen_ocode_ids():
    for i,n in enumerate(OPCODES):
        print "%s = %d" % (n, i)

def gen_opcode_repr():
    print "__REPR__ = [None] * __LENGTH__"
    for p in OPCODES[0:-1]:
        print "__REPR__[%s] = %s" % (p, ("\"%s\"" % p))

def gen_opcode_to_str():
    print \
"""
def opcode_to_str(p):
    return __REPR__[p]\n\n
""" 

gen_ocode_ids()
print "\n# ************************************************\n"
gen_opcode_repr()
print "\n# ************************************************"
gen_opcode_to_str()