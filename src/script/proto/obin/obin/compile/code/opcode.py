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
UNION = 18
LABEL = 19
STORE_LOCAL = 20
ITERATOR = 21
RETURN = 22
POP_CATCH = 23
CALL = 24
CALL_METHOD = 25
JUMP = 26
JUMP_IF_FALSE_NOPOP = 27
JUMP_IF_TRUE_NOPOP = 28
JUMP_IF_FALSE = 29
JUMP_IF_TRUE = 30
PUSH_CATCH = 31
JUMP_IF_ITERATOR_EMPTY = 32
METHOD = 33
MEMBER_DOT = 34
MEMBER = 35
POP = 36
THROW = 37
TYPE = 38
STORE_MEMBER = 39
SLICE = 40
IMPLEMENT = 41
UNPACK_SEQUENCE = 42
VECTOR = 43
TUPLE = 44
MAP = 45
LIST = 46
SPECIFY = 47

# ************************************************

__OPCODE_REPR__ = ["NIL", "TRUE", "FALSE", "LITERAL", "SYMBOL", "OUTER", "LOCAL", "IMPORTED", "FUNCTION", "INTEGER",
                   "DUP", "NEXT", "MODULE", "GENERIC", "ARGUMENTS", "FSELF", "FENV", "TRAIT", "UNION", "LABEL",
                   "STORE_LOCAL", "ITERATOR", "RETURN", "POP_CATCH", "CALL", "CALL_METHOD", "JUMP",
                   "JUMP_IF_FALSE_NOPOP", "JUMP_IF_TRUE_NOPOP", "JUMP_IF_FALSE", "JUMP_IF_TRUE", "PUSH_CATCH",
                   "JUMP_IF_ITERATOR_EMPTY", "METHOD", "MEMBER_DOT", "MEMBER", "POP", "THROW", "TYPE", "STORE_MEMBER",
                   "SLICE", "IMPLEMENT", "UNPACK_SEQUENCE", "VECTOR", "TUPLE", "MAP", "LIST", "SPECIFY", ]

# ************************************************

__UNKNOWN_CHANGE__ = -128

__STACK_CHANGES__ = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1,
                     -1, -1, -1, -1, -1, -1, -2, -3, -2, __UNKNOWN_CHANGE__, __UNKNOWN_CHANGE__, __UNKNOWN_CHANGE__,
                     __UNKNOWN_CHANGE__, __UNKNOWN_CHANGE__, __UNKNOWN_CHANGE__, ]


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
