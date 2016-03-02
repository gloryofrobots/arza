NIL = 0
TRUE = 1
FALSE = 2
LITERAL = 3
SYMBOL = 4
OUTER = 5
LOCAL = 6
IMPORTED = 7
FUNCTION = 8
INTEGER = 9
DUP = 10
NEXT = 11
MODULE = 12
GENERIC = 13
ARGUMENTS = 14
FSELF = 15
FENV = 16
TRAIT = 17
LABEL = 18
STORE_LOCAL = 19
ITERATOR = 20
RETURN = 21
POP_CATCH = 22
CALL = 23
CALL_METHOD = 24
JUMP = 25
JUMP_IF_FALSE_NOPOP = 26
JUMP_IF_TRUE_NOPOP = 27
JUMP_IF_FALSE = 28
JUMP_IF_TRUE = 29
PUSH_CATCH = 30
JUMP_IF_ITERATOR_EMPTY = 31
METHOD = 32
MEMBER_DOT = 33
MEMBER = 34
POP = 35
THROW = 36
STORE_MEMBER = 37
SLICE = 38
IMPLEMENT = 39
UNPACK_SEQUENCE = 40
VECTOR = 41
TUPLE = 42
MAP = 43
TYPE = 44
LIST = 45
SPECIFY = 46

# ************************************************

__OPCODE_REPR__ = ["NIL", "TRUE", "FALSE", "LITERAL", "SYMBOL", "OUTER", "LOCAL", "IMPORTED", "FUNCTION", "INTEGER",
                   "DUP", "NEXT", "MODULE", "GENERIC", "ARGUMENTS", "FSELF", "FENV", "TRAIT", "LABEL", "STORE_LOCAL",
                   "ITERATOR", "RETURN", "POP_CATCH", "CALL", "CALL_METHOD", "JUMP", "JUMP_IF_FALSE_NOPOP",
                   "JUMP_IF_TRUE_NOPOP", "JUMP_IF_FALSE", "JUMP_IF_TRUE", "PUSH_CATCH", "JUMP_IF_ITERATOR_EMPTY",
                   "METHOD", "MEMBER_DOT", "MEMBER", "POP", "THROW", "STORE_MEMBER", "SLICE", "IMPLEMENT",
                   "UNPACK_SEQUENCE", "VECTOR", "TUPLE", "MAP", "TYPE", "LIST", "SPECIFY", ]

# ************************************************

__UNKNOWN_CHANGE__ = -128

__STACK_CHANGES__ = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1,
                     -1, -1, -1, -1, -1, -2, -3, __UNKNOWN_CHANGE__, __UNKNOWN_CHANGE__, __UNKNOWN_CHANGE__,
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
    elif tag == UNPACK_SEQUENCE:
        return arg1 - 1
    elif tag == TUPLE:
        return -1 * arg1 + 1
    # pop generic from stack too
    elif tag == SPECIFY:
        return -1 * (arg1 + 1) + 1
    elif tag == TYPE:
        return -1 * arg1 + 2
    elif tag == IMPLEMENT:
        return -1 * arg1 + 2
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
    if tag >= JUMP and tag <= JUMP_IF_ITERATOR_EMPTY:
        return True
    return False


def is_label_opcode(tag):
    return tag == LABEL
