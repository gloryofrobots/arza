LOAD_UNDEFINED = 0
LOAD_NULL = 1
LOAD_TRUE = 2
LOAD_FALSE = 3
LOAD_LITERAL = 4
LOAD_OUTER = 5
LOAD_LOCAL = 6
LOAD_FUNCTION = 7
DUP = 8
NEXT_ITERATOR = 9
LABEL = 10
STORE_OUTER = 11
STORE_LOCAL = 12
LOAD_ITERATOR = 13
RETURN = 14
CALL_PRIMITIVE = 15
JUMP = 16
JUMP_IF_FALSE_NOPOP = 17
JUMP_IF_TRUE_NOPOP = 18
JUMP_IF_FALSE = 19
JUMP_IF_TRUE = 20
JUMP_IF_ITERATOR_EMPTY = 21
LOAD_MEMBER_DOT = 22
LOAD_MEMBER = 23
POP = 24
THROW = 25
STORE_MEMBER = 26
LOAD_VECTOR = 27
LOAD_OBJECT = 28
CALL = 29
CALL_METHOD = 30

# ************************************************

__OPCODE_REPR__ = ["LOAD_UNDEFINED", "LOAD_NULL", "LOAD_TRUE", "LOAD_FALSE", "LOAD_LITERAL", "LOAD_OUTER", "LOAD_LOCAL",
                   "LOAD_FUNCTION", "DUP", "NEXT_ITERATOR", "LABEL", "STORE_OUTER", "STORE_LOCAL", "LOAD_ITERATOR",
                   "RETURN", "CALL_PRIMITIVE", "JUMP", "JUMP_IF_FALSE_NOPOP", "JUMP_IF_TRUE_NOPOP", "JUMP_IF_FALSE",
                   "JUMP_IF_TRUE", "JUMP_IF_ITERATOR_EMPTY", "LOAD_MEMBER_DOT", "LOAD_MEMBER", "POP", "THROW",
                   "STORE_MEMBER", "LOAD_VECTOR", "LOAD_OBJECT", "CALL", "CALL_METHOD", ]

# ************************************************

__STACK_CHANGES__ = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, -1, -1, -1, -1, -2, None, None,
                     None, None, ]


# ************************************************

def opcode_to_str(p):
    return __OPCODE_REPR__[p]


# SOME OPCODES CHANGE STACK SIZE DEPENDING ON RUNTIME VALUES. MAXIMAL CHANGES USED FOR THIS OPCODES,
# SO STACK CAN BE LARGER THEN IT NECESSARY
def opcode_estimate_stack_change(opcode):
    tag = opcode[0]

    change = __STACK_CHANGES__[tag]
    if change is not None:
        return change

    arg1 = opcode[1]
    arg2 = opcode[2]

    if tag == CALL:
        return -1 * arg1 + 1
    if tag == CALL_METHOD:
        return -1 * arg1 + -1
    if tag == LOAD_OBJECT:
        return -1 * arg1 + arg2 + 1
    if tag == LOAD_VECTOR:
        return -1 * arg1 + 1


def opcode_info(routine, opcode):
    from obin.runtime.primitives import primitive_to_str

    tag = opcode[0]
    arg1 = opcode[1]
    arg2 = opcode[2]
    # ********************************
    if tag == LOAD_LOCAL:
        literal = routine.literals[arg2]
        return 'LOAD_LOCAL %s (%d)' % (literal, arg1)
    # ********************************
    elif tag == LOAD_OUTER:
        literal = routine.literals[arg2]
        return 'LOAD_OUTER %s (%d)' % (literal, arg1)
    # ********************************
    elif tag == LOAD_LITERAL:
        literal = routine.literals[arg1]
        return 'LOAD_OUTER %s (%d)' % (literal, arg1)
    # ********************************
    elif tag == STORE_LOCAL:
        literal = routine.literals[arg2]
        return 'STORE_LOCAL %s (%d)' % (literal, arg1)
    # ********************************
    elif tag == STORE_OUTER:
        literal = routine.literals[arg2]
        return 'STORE_OUTER %s (%d)' % (literal, arg1)
    # ********************************
    elif tag == CALL_PRIMITIVE:
        return 'CALL_PRIMITIVE %s ' % (primitive_to_str(arg1))
    else:
        return "<%s, %s, %s>" % (opcode_to_str(tag), str(arg1), str(arg2))


def is_jump_opcode(tag):
    if tag >= JUMP and tag <= JUMP_IF_ITERATOR_EMPTY:
        return True
    return False

def is_label_opcode(tag):
    return tag == LABEL
