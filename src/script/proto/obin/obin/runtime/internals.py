import math

from obin.runtime.error import ObinTypeError, ObinReferenceError
from obin.objects import api
from obin.objects.space import newnumber, isint, isstring, isfloat, newbool, newint, newfloat, newstring
from rpython.rlib.rarithmetic import ovfcheck, intmask
from rpython.rlib.rfloat import isnan, isinf
from rpython.rlib.objectmodel import specialize

from rpython.rlib.rfloat import NAN, INFINITY
# 15.7.3.2
w_MAX_VALUE = newnumber(1.7976931348623157e308)

# 15.7.3.3
w_MIN_VALUE = newnumber(5e-320)

# 15.7.3.4
w_NAN = newnumber(NAN)

# 15.7.3.5
w_POSITIVE_INFINITY = newnumber(INFINITY)

# 15.7.3.6
w_NEGATIVE_INFINITY = newnumber(-INFINITY)

# from rpython.rlib import jit


def plus(r, lprim, rprim):
    if isstring(lprim) or isstring(rprim):
        sleft = api.to_native_unicode(lprim)
        sright = api.to_native_unicode(rprim)
        return newstring(sleft + sright)
    # hot path
    if isint(lprim) and isint(rprim):
        ileft = api.to_native_integer(lprim)
        iright = api.to_native_integer(rprim)
        try:
            return newint(ovfcheck(ileft + iright))
        except OverflowError:
            return newfloat(float(ileft) + float(iright))
    else:
        fleft = api.to_native_float(lprim)
        fright = api.to_native_float(rprim)
        return newfloat(fleft + fright)


def sub(r, nleft, nright):
    if isint(nleft) and isint(nright):
        ileft = api.to_native_integer(nleft)
        iright = api.to_native_integer(nright)
        try:
            return newint(ovfcheck(ileft - iright))
        except OverflowError:
            return newfloat(float(ileft) - float(iright))

    fleft = api.to_native_float(nleft)
    fright = api.to_native_float(nright)
    return newfloat(fleft - fright)


def mult(r, nleft, nright):
    if isint(nleft) and isint(nright):
        ileft = api.to_native_integer(nleft)
        iright = api.to_native_integer(nright)
        try:
            return newint(ovfcheck(ileft * iright))
        except OverflowError:
            return newfloat(float(ileft) * float(iright))

    fleft = api.to_native_float(nleft)
    fright = api.to_native_float(nright)
    return newfloat(fleft * fright)


def mod(r, w_left, w_right):
    fleft = api.to_native_float(w_left)
    fright = api.to_native_float(w_right)

    if isnan(fleft) or isnan(fright):
        return w_NAN

    if isinf(fright) or fright == 0:
        return w_NAN

    if isinf(fright):
        return w_left

    if fleft == 0:
        return w_left

    return newfloat(math.fmod(fleft, fright))


def sign(x):
    from math import copysign
    return copysign(1.0, x)


def sign_of(a, b):
    sign_a = sign(a)
    sign_b = sign(b)
    return sign_a * sign_b


def w_signed_inf(sign):
    if sign < 0.0:
        return w_NEGATIVE_INFINITY
    return w_POSITIVE_INFINITY


# 11.5.2
def division(r, nleft, nright):
    fleft = api.to_native_float(nleft)
    fright = api.to_native_float(nright)
    if isnan(fleft) or isnan(fright):
        return w_NAN

    if isinf(fleft) and isinf(fright):
        return w_NAN

    if isinf(fleft) and fright == 0:
        s = sign_of(fleft, fright)
        return w_signed_inf(s)

    if isinf(fright):
        return newfloat(0.0)

    if fleft == 0 and fright == 0:
        return w_NAN

    if fright == 0:
        s = sign_of(fleft, fright)
        return w_signed_inf(s)

    val = fleft / fright
    return newfloat(val)


@specialize.argtype(0, 1)
def _compare_gt(x, y):
    return x > y


@specialize.argtype(0, 1)
def _compare_ge(x, y):
    return x >= y


def _base_compare(x, y, _compare):
    if isint(x) and isint(y):
        n1 = api.to_native_integer(x)
        n2 = api.to_native_integer(y)
        return _compare(n1, n2)

    if isfloat(x) and isfloat(y):
        n1 = api.to_native_float(x)
        n2 = api.to_native_float(y)
        return _compare(n1, n2)

    if isstring(x) and isstring(y):
        n1 = api.to_native_string(x)
        n2 = api.to_native_string(y)
        return _compare(n1, n2)
    else:
        raise ObinTypeError(u"Invalid comparison operation")


def compare_gt(r, x, y):
    return newbool(_base_compare(x, y, _compare_gt))


def compare_ge(r, x, y):
    return newbool(_base_compare(x, y, _compare_ge))


def compare_lt(r, x, y):
    return newbool(_base_compare(y, x, _compare_gt))


def compare_le(r, x, y):
    return newbool(_base_compare(y, x, _compare_ge))


def uminus(routine, obj):
    if isint(obj):
        intval = api.to_native_integer(obj)
        if intval == 0:
            return newfloat(-float(intval))
        return newint(-intval)
    n1 = api.to_native_float(obj)
    return newfloat(-n1)


def _in(routine, left, right):
    from obin.objects.space import iscell
    if not iscell(right):
        raise ObinTypeError(u"TypeError: invalid object for in operator")

    return api.contains(right, left)


def _bitand(r, op1, op2):
    return newint(int(op1 & op2))


def _bitxor(r, op1, op2):
    return newint(int(op1 ^ op2))


def _bitor(r, op1, op2):
    return newint(int(op1 | op2))


def bitnot(r, op):
    return newint(~op)


def ursh(r, lval, rval):
    lnum = api.to_native_integer(lval)
    rnum = api.to_native_integer(rval)

    # from rpython.rlib.rarithmetic import ovfcheck_float_to_int

    shift_count = rnum & 0x1F
    res = lnum >> shift_count
    return newnumber(res)


def rsh(r, lval, rval):
    lnum = api.to_native_integer(lval)
    rnum = api.to_native_integer(rval)

    # from rpython.rlib.rarithmetic import ovfcheck_float_to_int

    shift_count = rnum & 0x1F
    res = lnum >> shift_count
    return newnumber(res)


def lsh(r, lval, rval):
    lnum = api.to_native_integer(lval)
    rnum = api.to_native_integer(rval)

    shift_count = intmask(rnum & 0x1F)
    res = lnum << shift_count

    return newnumber(res)


def uplus(r, op1):
    assert isint(op1)
    return op1


def _not(r, val):
    v = api.to_native_bool(val)
    return newbool(not v)


def eq(r, op1, op2):
    return api.equal(op1, op2)


def noteq(r, op1, op2):
    # TODO api.ne
    return newbool(not api.to_native_bool(api.equal(op1, op2)))


def _isnot(r, op1, op2):
    # TODO api.isnot
    return newbool(not api.to_native_bool(api.strict_equal(op1, op2)))


def _is(r, op1, op2):
    return api.strict_equal(op1, op2)


"""
********************************** WRAPPERS
"""


def apply_binary_on_unboxed_integers(routine, operation):
    right = api.to_native_integer(routine.stack.pop())
    left = api.to_native_integer(routine.stack.pop())
    routine.stack.push(operation(routine, left, right))


def apply_binary(routine, operation):
    right = routine.stack.pop()
    left = routine.stack.pop()
    routine.stack.push(operation(routine, left, right))


def apply_unary(routine, operation):
    val = routine.stack.pop()
    routine.stack.push(operation(routine, val))


def apply_unary_on_unboxed_integer(routine, operation):
    val = api.to_native_integer(routine.stack.pop())
    routine.stack.push(operation(routine, val))


def internal_IN(routine):
    apply_binary(routine, _in)


def internal_SUB(routine):
    apply_binary(routine, sub)


def internal_ADD(routine):
    apply_binary(routine, plus)


def internal_MUL(routine):
    apply_binary(routine, mult)


def internal_DIV(routine):
    apply_binary(routine, division)


def internal_MOD(routine):
    apply_binary(routine, mod)


def internal_BITAND(routine):
    apply_binary_on_unboxed_integers(routine, _bitand)


def internal_BITXOR(routine):
    apply_binary_on_unboxed_integers(routine, _bitxor)


def internal_BITOR(routine):
    apply_binary_on_unboxed_integers(routine, _bitor)


def internal_BITNOT(routine):
    apply_unary_on_unboxed_integer(routine, bitnot)


def internal_URSH(routine):
    apply_binary(routine, ursh)


def internal_RSH(routine):
    apply_binary(routine, rsh)


def internal_LSH(routine):
    apply_binary(routine, lsh)


def internal_UPLUS(routine):
    apply_unary(routine, uplus)


def internal_UMINUS(routine):
    apply_unary(routine, uminus)


def internal_NOT(routine):
    apply_unary(routine, _not)


def internal_GT(routine):
    apply_binary(routine, compare_gt)


def internal_GE(routine):
    apply_binary(routine, compare_ge)


def internal_LT(routine):
    apply_binary(routine, compare_lt)


def internal_LE(routine):
    apply_binary(routine, compare_le)


def internal_EQ(routine):
    apply_binary(routine, eq)


def internal_NE(routine):
    apply_binary(routine, noteq)


def internal_IS(routine):
    apply_binary(routine, _is)


def internal_ISNOT(routine):
    apply_binary(routine, _isnot)


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
