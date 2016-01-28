UNDEFINED = 0
NULL = 1
TRUE = 2
FALSE = 3
LITERAL = 4
SYMBOL = 5
OUTER = 6
LOCAL = 7
FUNCTION = 8
INTEGER = 9
DUP = 10
NEXT = 11
LOAD = 12
USE = 13
MODULE = 14
GENERIC = 15
TRAIT = 16
ARGUMENTS = 17
LABEL = 18
STORE_LOCAL = 19
ITERATOR = 20
RETURN = 21
POP_CATCH = 22
CALL_INTERNAL = 23
CALL = 24
CALL_METHOD = 25
JUMP = 26
JUMP_IF_FALSE_NOPOP = 27
JUMP_IF_TRUE_NOPOP = 28
JUMP_IF_FALSE = 29
JUMP_IF_TRUE = 30
PUSH_CATCH = 31
JUMP_IF_ITERATOR_EMPTY = 32
MEMBER_DOT = 33
MEMBER = 34
POP = 35
THROW = 36
STORE_MEMBER = 37
SLICE = 38
UNPACK_SEQUENCE = 39
VECTOR = 40
TUPLE = 41
MAP = 42
LIST = 43
SPECIFY = 44

# ************************************************

__OPCODE_REPR__ = ["UNDEFINED", "NULL", "TRUE", "FALSE", "LITERAL", "SYMBOL", "OUTER", "LOCAL", "FUNCTION", "INTEGER",
                   "DUP", "NEXT", "LOAD", "USE", "MODULE", "GENERIC", "TRAIT", "ARGUMENTS", "LABEL", "STORE_LOCAL",
                   "ITERATOR", "RETURN", "POP_CATCH", "CALL_INTERNAL", "CALL", "CALL_METHOD", "JUMP",
                   "JUMP_IF_FALSE_NOPOP", "JUMP_IF_TRUE_NOPOP", "JUMP_IF_FALSE", "JUMP_IF_TRUE", "PUSH_CATCH",
                   "JUMP_IF_ITERATOR_EMPTY", "MEMBER_DOT", "MEMBER", "POP", "THROW", "STORE_MEMBER", "SLICE",
                   "UNPACK_SEQUENCE", "VECTOR", "TUPLE", "MAP", "LIST", "SPECIFY", ]

# ************************************************

__UNKNOWN_CHANGE__ = -128

__STACK_CHANGES__ = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, -1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                     -1, -1, -1, -1, -1, -2, -3, __UNKNOWN_CHANGE__, __UNKNOWN_CHANGE__, __UNKNOWN_CHANGE__,
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
    from obin.builtins.internals.internals import internal_to_str

    tag = opcode[0]
    arg1 = opcode[1]
    arg2 = opcode[2]
    # ********************************
    if tag == LOCAL:
        literal = routine.literals[arg2]
        return 'LOCAL %s (%d)' % (literal, arg1)
    # ********************************
    elif tag == OUTER:
        literal = routine.literals[arg2]
        return 'OUTER %s (%d)' % (literal, arg1)
    # ********************************
    elif tag == LITERAL:
        literal = routine.literals[arg1]
        return 'LITERAL %s (%d)' % (literal, arg1)
    # ********************************
    elif tag == STORE_LOCAL:
        literal = routine.literals[arg2]
        return 'STORE_LOCAL %s (%d)' % (literal, arg1)
    # ********************************
    elif tag == LOAD:
        literal = routine.literals[arg1]
        return 'LOAD %s' % (literal,)
    # ********************************
    elif tag == CALL_INTERNAL:
        return 'CALL_PRIMITIVE %s ' % (internal_to_str(arg1))
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
