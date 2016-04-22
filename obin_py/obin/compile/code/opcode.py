VOID = 0
TRUE = 1
FALSE = 2
LITERAL = 3
INT = 4
FLOAT = 5
STRING = 6
CHAR = 7
SYMBOL = 8
OUTER = 9
LOCAL = 10
TEMPORARY = 11
IMPORT_NAME = 12
FUNCTION = 13
DUP = 14
FARGS = 15
FSELF = 16
FENV = 17
LABEL = 18
STORE_LOCAL = 19
STORE_TEMPORARY = 20
RETURN = 21
POP_CATCH = 22
CALL = 23
JUMP = 24
JUMP_IF_FALSE_NOPOP = 25
JUMP_IF_TRUE_NOPOP = 26
JUMP_IF_FALSE = 27
PUSH_CATCH = 28
JUMP_IF_TRUE = 29
POP = 30
THROW = 31
UNPACK_TUPLE = 32
VECTOR = 33
TUPLE = 34
MAP = 35
LIST = 36

# ************************************************

__OPCODE_REPR__ = ["VOID", "TRUE", "FALSE", "LITERAL", "INT", "FLOAT", "STRING", "CHAR", "SYMBOL", "OUTER", "LOCAL",
                   "TEMPORARY", "IMPORT_NAME", "FUNCTION", "DUP", "FARGS", "FSELF", "FENV", "LABEL", "STORE_LOCAL",
                   "STORE_TEMPORARY", "RETURN", "POP_CATCH", "CALL", "JUMP", "JUMP_IF_FALSE_NOPOP",
                   "JUMP_IF_TRUE_NOPOP", "JUMP_IF_FALSE", "PUSH_CATCH", "JUMP_IF_TRUE", "POP", "THROW", "UNPACK_TUPLE",
                   "VECTOR", "TUPLE", "MAP", "LIST", ]

# ************************************************

__UNKNOWN_CHANGE__ = -128

__STACK_CHANGES__ = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, -1,
                     __UNKNOWN_CHANGE__, __UNKNOWN_CHANGE__, __UNKNOWN_CHANGE__, __UNKNOWN_CHANGE__,
                     __UNKNOWN_CHANGE__, ]


# ************************************************

def opcode_to_str(p):
    return __OPCODE_REPR__[p]


# SOME OPCODES CHANGE STACK SIZE DEPENDING ON RUNTIME VALUES. MAXIMAL CHANGES USED FOR THIS OPCODES,
# SO STACK CAN BE LARGER THEN IT NECESSARY
def opcode_estimate_stack_change(opcode):
    assert isinstance(opcode, tuple)
    assert len(opcode) == 3
    tag = opcode[0]
    assert isinstance(tag, int)

    change = __STACK_CHANGES__[tag]
    # print opcode_to_str(tag), change
    if change != __UNKNOWN_CHANGE__:
        return change

    arg1 = opcode[1]
    arg2 = opcode[2]

    assert isinstance(arg1, int)
    assert isinstance(arg2, int)

    if tag == MAP:
        return -1 * arg1 + 1
    elif tag == VECTOR:
        return -1 * arg1 + 1
    elif tag == UNPACK_TUPLE:
        return arg1 - 1
    elif tag == TUPLE:
        return -1 * arg1 + 1
    return 0


def opcode_info(routine, opcode):
    tag = opcode[0]
    arg1 = opcode[1]
    arg2 = opcode[2]
    # ********************************
    if tag == LOCAL:
        literal = routine.env.literals[arg2]
        return 'LOCAL %s (%d)' % (literal, arg1)
    # ********************************
    elif tag == OUTER:
        literal = routine.env.literals[arg2]
        return 'OUTER %s (%d)' % (literal, arg1)
    # ********************************
    elif tag == LITERAL:
        literal = routine.env.literals[arg1]
        return 'LITERAL %s (%d)' % (literal, arg1)
    # ********************************
    elif tag == STORE_LOCAL:
        literal = routine.env.literals[arg2]
        return 'STORE_LOCAL %s (%d)' % (literal, arg1)
    # ********************************
    elif tag == FUNCTION:
        return 'LOAD_FUNCTION'
    else:
        return "<%s, %s, %s>" % (opcode_to_str(tag), str(arg1), str(arg2))


def is_jump_opcode(tag):
    if tag >= JUMP and tag <= JUMP_IF_TRUE:
        return True
    return False


def is_label_opcode(tag):
    return tag == LABEL
