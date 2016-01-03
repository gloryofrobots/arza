from operations import *

from obin.objects.space import newvector, isnumber, isint, isentity, isboolean


def call2(process, generic, l, r):
    api.call(process, generic, newvector([l, r]))


def call1(process, generic, w):
    api.call(process, generic, newvector([w]))


# TODO INLINE
def is_both_numbers(w1, w2):
    return isnumber(w1) and isnumber(w2)


def is_both_integers(w1, w2):
    return isint(w1) and isint(w2)


def is_both_strings(w1, w2):
    return isstring(w1) and isstring(w2)


def is_not_entities(w1, w2):
    return not isentity(w1) and not isentity(w2)


def apply_binary(process, routine, operation, left, right):
    routine.stack.push(operation(process, left, right))


def apply_unary(process, routine, operation, val):
    routine.stack.push(operation(process, val))


def internal_SUB(process, routine):
    right = routine.stack.pop()
    left = routine.stack.pop()

    if is_both_numbers(left, right):
        apply_binary(process, routine, sub_n_n, left, right)
    else:
        call2(process, process.stdlib.generics.Sub, left, right)


def internal_ADD(process, routine):
    right = routine.stack.pop()
    left = routine.stack.pop()

    if is_both_numbers(left, right):
        apply_binary(process, routine, add_n_n, left, right)
    elif is_both_strings(left, right):
        apply_binary(process, routine, add_s_s, left, right)
    else:
        call2(process, process.stdlib.generics.Add, left, right)


def internal_MUL(process, routine):
    right = routine.stack.pop()
    left = routine.stack.pop()

    if is_both_numbers(left, right):
        apply_binary(process, routine, mult_n_n, left, right)
    else:
        call2(process, process.stdlib.generics.Mul, left, right)


def internal_DIV(process, routine):
    right = routine.stack.pop()
    left = routine.stack.pop()

    if is_both_numbers(left, right):
        apply_binary(process, routine, div_n_n, left, right)
    else:
        call2(process, process.stdlib.generics.Div, left, right)


def internal_MOD(process, routine):
    right = routine.stack.pop()
    left = routine.stack.pop()

    if is_both_numbers(left, right):
        apply_binary(process, routine, mod_n_n, left, right)
    else:
        call2(process, process.stdlib.generics.Mod, left, right)


def internal_BITAND(process, routine):
    right = routine.stack.pop()
    left = routine.stack.pop()

    if is_both_integers(left, right):
        apply_binary(process, routine, bitand_i_i, left, right)
    else:
        call2(process, process.stdlib.generics.BitAnd, left, right)


def internal_BITXOR(process, routine):
    right = routine.stack.pop()
    left = routine.stack.pop()

    if is_both_integers(left, right):
        apply_binary(process, routine, bitxor_i_i, left, right)
    else:
        call2(process, process.stdlib.generics.BitXor, left, right)


def internal_BITOR(process, routine):
    right = routine.stack.pop()
    left = routine.stack.pop()

    if is_both_integers(left, right):
        apply_binary(process, routine, bitor_i_i, left, right)
    else:
        call2(process, process.stdlib.generics.BitOr, left, right)


def internal_BITNOT(process, routine):
    value = routine.stack.pop()
    apply_unary(process, routine, bitnot_i, value)

    if isint(value):
        apply_unary(process, routine, bitnot_i, value)
    else:
        call1(process, process.stdlib.generics.BitNot, value)


def internal_URSH(process, routine):
    right = routine.stack.pop()
    left = routine.stack.pop()

    if is_both_integers(left, right):
        apply_binary(process, routine, ursh_i_i, left, right)
    else:
        call2(process, process.stdlib.generics.UnsignedRightShift, left, right)


def internal_RSH(process, routine):
    right = routine.stack.pop()
    left = routine.stack.pop()

    if is_both_integers(left, right):
        apply_binary(process, routine, rsh_i_i, left, right)
    else:
        call2(process, process.stdlib.generics.RightShift, left, right)


def internal_LSH(process, routine):
    right = routine.stack.pop()
    left = routine.stack.pop()

    if is_both_integers(left, right):
        apply_binary(process, routine, lsh_i_i, left, right)
    else:
        call2(process, process.stdlib.generics.LeftShift, left, right)


def internal_UPLUS(process, routine):
    value = routine.stack.pop()
    apply_unary(process, routine, uplus_n, value)

    if isnumber(value):
        apply_unary(process, routine, uplus_n, value)
    else:
        call1(process, process.stdlib.generics.UnaryPlus, value)


def internal_UMINUS(process, routine):
    value = routine.stack.pop()

    if isnumber(value):
        apply_unary(process, routine, uminus_n, value)
    else:
        call1(process, process.stdlib.generics.UnaryMinus, value)


def internal_GT(process, routine):
    right = routine.stack.pop()
    left = routine.stack.pop()

    if is_both_numbers(left, right):
        apply_binary(process, routine, compare_gt_n_n, left, right)
    else:
        call2(process, process.stdlib.generics.GreaterThen, left, right)


def internal_GE(process, routine):
    right = routine.stack.pop()
    left = routine.stack.pop()

    if is_both_numbers(left, right):
        apply_binary(process, routine, compare_ge_n_n, left, right)
    else:
        call2(process, process.stdlib.generics.GreaterEqual, left, right)


def internal_LT(process, routine):
    right = routine.stack.pop()
    left = routine.stack.pop()

    if is_both_numbers(left, right):
        apply_binary(process, routine, compare_gt_n_n, right, left)
    else:
        call2(process, process.stdlib.generics.GreaterThen, right, left)


def internal_LE(process, routine):
    right = routine.stack.pop()
    left = routine.stack.pop()

    if is_both_numbers(left, right):
        apply_binary(process, routine, compare_ge_n_n, right, left)
    else:
        call2(process, process.stdlib.generics.GreaterEqual, right, left)


def internal_EQ(process, routine):
    right = routine.stack.pop()
    left = routine.stack.pop()
    if is_not_entities(left, right):
        apply_binary(process, routine, eq_w, left, right)
    else:
        call2(process, process.stdlib.generics.Equal, left, right)


def internal_NE(process, routine):
    right = routine.stack.pop()
    left = routine.stack.pop()
    if is_not_entities(left, right):
        apply_binary(process, routine, noteq_w, left, right)
    else:
        call2(process, process.stdlib.generics.NotEqual, left, right)


def internal_NOT(process, routine):
    value = routine.stack.pop()
    apply_unary(process, routine, not_w, value)


def internal_IN(process, routine):
    right = routine.stack.pop()
    left = routine.stack.pop()

    if is_not_entities(left, right):
        apply_binary(process, routine, in_w, left, right)
    else:
        call2(process, process.stdlib.generics.In, left, right)


def internal_IS(process, routine):
    right = routine.stack.pop()
    left = routine.stack.pop()
    apply_binary(process, routine, is_w, left, right)


def internal_ISNOT(process, routine):
    right = routine.stack.pop()
    left = routine.stack.pop()
    apply_binary(process, routine, isnot_w, left, right)


# ********************  INTERNALS IDS ********************
IS = 0
NE = 1
EQ = 2
NOT = 3
ISNOT = 4
IN = 5
ADD = 6
MOD = 7
MUL = 8
DIV = 9
SUB = 10
UMINUS = 11
UPLUS = 12
GE = 13
GT = 14
LT = 15
LE = 16
BITNOT = 17
BITOR = 18
BITXOR = 19
BITAND = 20
LSH = 21
RSH = 22
URSH = 23
__LENGTH__ = 24


# ********************* INTERNALS REPR ***************
__INTERNALS_REPR__ = [None] * __LENGTH__
__INTERNALS_REPR__[IS] = "IS"
__INTERNALS_REPR__[NE] = "NE"
__INTERNALS_REPR__[EQ] = "EQ"
__INTERNALS_REPR__[NOT] = "NOT"
__INTERNALS_REPR__[ISNOT] = "ISNOT"
__INTERNALS_REPR__[IN] = "IN"
__INTERNALS_REPR__[ADD] = "ADD"
__INTERNALS_REPR__[MOD] = "MOD"
__INTERNALS_REPR__[MUL] = "MUL"
__INTERNALS_REPR__[DIV] = "DIV"
__INTERNALS_REPR__[SUB] = "SUB"
__INTERNALS_REPR__[UMINUS] = "UMINUS"
__INTERNALS_REPR__[UPLUS] = "UPLUS"
__INTERNALS_REPR__[GE] = "GE"
__INTERNALS_REPR__[GT] = "GT"
__INTERNALS_REPR__[LT] = "LT"
__INTERNALS_REPR__[LE] = "LE"
__INTERNALS_REPR__[BITNOT] = "BITNOT"
__INTERNALS_REPR__[BITOR] = "BITOR"
__INTERNALS_REPR__[BITXOR] = "BITXOR"
__INTERNALS_REPR__[BITAND] = "BITAND"
__INTERNALS_REPR__[LSH] = "LSH"
__INTERNALS_REPR__[RSH] = "RSH"
__INTERNALS_REPR__[URSH] = "URSH"


def newinternals():
    P = [None] * __LENGTH__

    P[IS] = internal_IS
    P[NE] = internal_NE
    P[EQ] = internal_EQ
    P[NOT] = internal_NOT
    P[ISNOT] = internal_ISNOT
    P[IN] = internal_IN
    P[ADD] = internal_ADD
    P[MOD] = internal_MOD
    P[MUL] = internal_MUL
    P[DIV] = internal_DIV
    P[SUB] = internal_SUB
    P[UMINUS] = internal_UMINUS
    P[UPLUS] = internal_UPLUS
    P[GE] = internal_GE
    P[GT] = internal_GT
    P[LT] = internal_LT
    P[LE] = internal_LE
    P[BITNOT] = internal_BITNOT
    P[BITOR] = internal_BITOR
    P[BITXOR] = internal_BITXOR
    P[BITAND] = internal_BITAND
    P[LSH] = internal_LSH
    P[RSH] = internal_RSH
    P[URSH] = internal_URSH
    return P


__INTERNALS__ = newinternals()


def internal_to_str(p):
    return __INTERNALS_REPR__[p]


def get_internal(id):
    return __INTERNALS__[id]
