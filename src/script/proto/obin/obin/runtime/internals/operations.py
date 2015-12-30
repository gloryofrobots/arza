import math

from obin.runtime.error import ObinTypeError, ObinReferenceError
from obin.objects import api
from obin.objects.space import newnumber, isint, isstring, isfloat, \
    newbool, newint, newfloat, newstring, newvector, isnumber, is_both_numbers
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


def add_string_string(process, l, r):
    sleft = api.to_native_unicode(l)
    sright = api.to_native_unicode(r)
    return newstring(sleft + sright)


def add_int_int(process, l, r):
    ileft = api.to_native_integer(l)
    iright = api.to_native_integer(r)
    try:
        return newint(ovfcheck(ileft + iright))
    except OverflowError:
        return newfloat(float(ileft) + float(iright))


def add_float_float(process, l, r):
    fleft = api.to_native_float(l)
    fright = api.to_native_float(r)
    return newfloat(fleft + fright)


def plus_n_n(process, lprim, rprim):
    if isstring(lprim) or isstring(rprim):
        return add_string_string(process, lprim, rprim)

    if isint(lprim) and isint(rprim):
        return add_int_int(process, lprim, rprim)
    else:
        return add_float_float(process, lprim, rprim)


def sub_int_int(nleft, nright):
    ileft = api.to_native_integer(nleft)
    iright = api.to_native_integer(nright)
    try:
        return newint(ovfcheck(ileft - iright))
    except OverflowError:
        return newfloat(float(ileft) - float(iright))


def sub_float_float(nleft, nright):
    fleft = api.to_native_float(nleft)
    fright = api.to_native_float(nright)
    return newfloat(fleft - fright)


def sub_n_n(process, nleft, nright):
    if isint(nleft) and isint(nright):
        return sub_int_int(nleft, nright)
    return sub_float_float(nleft, nright)


def mult_f_f(process, nleft, nright):
    fleft = api.to_native_float(nleft)
    fright = api.to_native_float(nright)
    return newfloat(fleft * fright)


def mult_i_i(process, nleft, nright):
    ileft = api.to_native_integer(nleft)
    iright = api.to_native_integer(nright)
    try:
        return newint(ovfcheck(ileft * iright))
    except OverflowError:
        return newfloat(float(ileft) * float(iright))


def mult_n_n(process, nleft, nright):
    if isint(nleft) and isint(nright):
        return mult_i_i(process, nleft, nright)
    return mult_f_f(process, nleft, nright)


def div_i_i(process, nleft, nright):
    ileft = api.to_native_integer(nleft)
    iright = api.to_native_integer(nright)
    try:
        z = ovfcheck(ileft // iright)
    except ZeroDivisionError:
        raise RuntimeError("ZeroDivision")
    return newint(z)


def div_f_f(process, nleft, nright):
    # TODO EXCEPTIONS
    fleft = api.to_native_float(nleft)
    fright = api.to_native_float(nright)

    if isnan(fleft) or isnan(fright):
        return w_NAN

    if isinf(fleft) and isinf(fright):
        return w_NAN

    if isinf(fright):
        return newfloat(0.0)

    try:
        val = fleft / fright
    except ZeroDivisionError:
        raise RuntimeError("ZeroDivision")

    return newfloat(val)


def div_n_n(process, nleft, nright):
    if isint(nleft) and isint(nright):
        return div_i_i(process, nleft, nright)

    return div_f_f(process, nleft, nright)


def mod_f_f(process, nleft, nright):
    fleft = api.to_native_float(nleft)
    fright = api.to_native_float(nright)

    if isnan(fleft) or isnan(fright):
        return w_NAN

    if isinf(fright) or fright == 0:
        return w_NAN

    if isinf(fright):
        return nleft

    if fleft == 0:
        return nleft

    return newfloat(math.fmod(fleft, fright))


def mod_n_n(process, nleft, nright):
    mod_f_f(process, nleft, nright)


def uminus_float(process, obj):
    n1 = api.to_native_float(obj)
    return newfloat(-n1)


def uminus_int(process, obj):
    intval = api.to_native_integer(obj)
    if intval == 0:
        return newfloat(-float(intval))
    return newint(-intval)


def uminus_n(process, obj):
    if isint(obj):
        return uminus_int(process, obj)
    return uminus_float(process, obj)


def compare_gt_int_int(process, w_x, w_y):
    x = api.to_native_integer(w_x)
    y = api.to_native_integer(w_y)
    return newbool(x > y)


def compare_gt_float_float(process, w_x, w_y):
    x = api.to_native_float(w_x)
    y = api.to_native_float(w_y)
    return newbool(x > y)


def compare_gt_n_n(process, x, y):
    if isint(x) and isint(y):
        return compare_gt_int_int(process, x, y)
    if isfloat(x) and isfloat(y):
        return compare_gt_float_float(process, x, y)
    assert False


def compare_ge_int_int(process, w_x, w_y):
    x = api.to_native_integer(w_x)
    y = api.to_native_integer(w_y)
    return newbool(x >= y)


def compare_ge_float_float(process, w_x, w_y):
    x = api.to_native_float(w_x)
    y = api.to_native_float(w_y)
    return newbool(x >= y)


def compare_ge_n_n(process, x, y):
    if isint(x) and isint(y):
        return compare_ge_int_int(process, x, y)
    if isfloat(x) and isfloat(y):
        return compare_ge_float_float(process, x, y)
    assert False


def in_w(process, routine, left, right):
    from obin.objects.space import iscell
    if not iscell(right):
        raise ObinTypeError(u"TypeError: invalid object for in operator")

    return api.contains(right, left)


def bitand_int_int(process, op1_w, op2_w):
    op1 = api.to_native_integer(op1_w)
    op2 = api.to_native_integer(op2_w)
    return newint(int(op1 & op2))


def bitxor_int_int(process, op1_w, op2_w):
    op1 = api.to_native_integer(op1_w)
    op2 = api.to_native_integer(op2_w)
    return newint(int(op1 ^ op2))


def bitor_int_int(process, op1_w, op2_w):
    op1 = api.to_native_integer(op1_w)
    op2 = api.to_native_integer(op2_w)
    return newint(int(op1 | op2))


def bitnot_int(process, op1_w):
    op = api.to_native_integer(op1_w)
    return newint(~op)


def ursh_int_int(process, lval, rval):
    lnum = api.to_native_integer(lval)
    rnum = api.to_native_integer(rval)

    # from rpython.rlib.rarithmetic import ovfcheck_float_to_int

    shift_count = rnum & 0x1F
    res = lnum >> shift_count
    return newnumber(res)


def rsh_int_int(process, lval, rval):
    lnum = api.to_native_integer(lval)
    rnum = api.to_native_integer(rval)

    # from rpython.rlib.rarithmetic import ovfcheck_float_to_int

    shift_count = rnum & 0x1F
    res = lnum >> shift_count
    return newnumber(res)


def lsh_int_int(process, lval, rval):
    lnum = api.to_native_integer(lval)
    rnum = api.to_native_integer(rval)

    shift_count = intmask(rnum & 0x1F)
    res = lnum << shift_count

    return newnumber(res)


def uplus_n(process, op1):
    return op1


def not_w(process, val):
    v = api.to_native_bool(val)
    return newbool(not v)


def eq_w(process, op1, op2):
    return api.equal(op1, op2)


def noteq_w(process, op1, op2):
    # TODO api.ne
    return newbool(not api.to_native_bool(api.equal(op1, op2)))


def isnot_w(process, op1, op2):
    # TODO api.isnot
    return newbool(not api.to_native_bool(api.strict_equal(op1, op2)))


def is_w(process, op1, op2):
    return api.strict_equal(op1, op2)
