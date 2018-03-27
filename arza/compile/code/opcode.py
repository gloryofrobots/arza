VOID = 0
NIL = 1
TRUE = 2
FALSE = 3
LITERAL = 4
OUTER = 5
LOCAL = 6
TEMPORARY = 7
IMPORT_NAME = 8
FUNCTION = 9
DUP = 10
LOOKUP = 11
FARGS = 12
FSELF = 13
LABEL = 14
STORE_LOCAL_CONST = 15
STORE_LOCAL_VAR = 16
STORE_TEMPORARY = 17
RETURN = 18
POP_CATCH = 19
CALL = 20
JUMP = 21
JUMP_IF_FALSE_NOPOP = 22
JUMP_IF_TRUE_NOPOP = 23
JUMP_IF_FALSE = 24
PUSH_CATCH = 25
JUMP_IF_TRUE = 26
POP = 27
THROW = 28
UNPACK_TUPLE = 29
VECTOR = 30
TUPLE = 31
MAP = 32
LIST = 33

# ************************************************

__OPCODE_REPR__ = ["VOID", "NIL", "TRUE", "FALSE", "LITERAL", "OUTER", "LOCAL", "TEMPORARY", "IMPORT_NAME", "FUNCTION",
                   "DUP", "LOOKUP", "FARGS", "FSELF", "LABEL", "STORE_LOCAL_CONST", "STORE_LOCAL_VAR",
                   "STORE_TEMPORARY", "RETURN", "POP_CATCH", "CALL", "JUMP", "JUMP_IF_FALSE_NOPOP",
                   "JUMP_IF_TRUE_NOPOP", "JUMP_IF_FALSE", "PUSH_CATCH", "JUMP_IF_TRUE", "POP", "THROW", "UNPACK_TUPLE",
                   "VECTOR", "TUPLE", "MAP", "LIST", ]

# ************************************************

__UNKNOWN_CHANGE__ = -128

__STACK_CHANGES__ = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, -1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, -1,
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
    elif tag == STORE_LOCAL_CONST:
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
