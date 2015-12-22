from obin.compile.code.opcode import *
# ************************************************

__OPCODE_REPR__ = ["UNDEFINED", "NULL", "TRUE", "FALSE", "LITERAL", "OUTER", "LOCAL", "FUNCTION", "INTEGER", "DUP",
                   "ITERATOR_NEXT", "IMPORT", "IMPORT_MEMBER", "GENERIC", "TRAIT", "LABEL", "STORE_OUTER",
                   "STORE_LOCAL", "ITERATOR", "RETURN", "CALL_PRIMITIVE", "CALL", "CALL_METHOD", "JUMP",
                   "JUMP_IF_FALSE_NOPOP", "JUMP_IF_TRUE_NOPOP", "JUMP_IF_FALSE", "JUMP_IF_TRUE",
                   "JUMP_IF_ITERATOR_EMPTY", "MEMBER_DOT", "MEMBER", "POP", "THROW", "CONCAT", "STORE_MEMBER",
                   "PUSH_MANY", "VECTOR", "TUPLE", "OBJECT", "REIFY", ]

# ************************************************

__STACK_CHANGES__ = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, -1, -1, -1,
                     -1, -1, -2, None, None, None, None, None, ]


# ************************************************

def opcode_to_str(p):
    return __OPCODE_REPR__[p]


# SOME OPCODES CHANGE STACK SIZE DEPENDING ON RUNTIME VALUES. MAXIMAL CHANGES USED FOR THIS OPCODES,
# SO STACK CAN BE LARGER THEN IT NECESSARY
def opcode_estimate_stack_change(opcode):
    tag = opcode[0]

    change = __STACK_CHANGES__[tag]
    # print opcode_to_str(tag), change
    if change is not None:
        return change

    arg1 = opcode[1]
    arg2 = opcode[2]

    if tag == PUSH_MANY:
        return -1 * arg1 + 1
    elif tag == OBJECT:
        return -1 * arg1 + arg2 + 1
    elif tag == VECTOR:
        return -1 * arg1 + 1
    elif tag == TUPLE:
        return -1 * arg1 + 1
    # pop generic from stack too
    elif tag == REIFY:
        return -1 * (arg1 + 1) + 1


def opcode_info(routine, opcode):
    from obin.runtime.primitives import primitive_to_str

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
        return 'OUTER %s (%d)' % (literal, arg1)
    # ********************************
    elif tag == STORE_LOCAL:
        literal = routine.literals[arg2]
        return 'STORE_LOCAL %s (%d)' % (literal, arg1)
    # ********************************
    elif tag == STORE_OUTER:
        literal = routine.literals[arg2]
        return 'STORE_OUTER %s (%d)' % (literal, arg1)
    # ********************************
    elif tag == IMPORT:
        literal = routine.literals[arg1]
        return 'IMPORT %s' % (literal,)
    # ********************************
    elif tag == IMPORT_MEMBER:
        literal = routine.literals[arg1]
        return 'IMPORT_MEMBER %s' % (literal,)
    # ********************************
    elif tag == CALL_PRIMITIVE:
        return 'CALL_PRIMITIVE %s ' % (primitive_to_str(arg1))
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
