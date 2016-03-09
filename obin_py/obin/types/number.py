__author__ = 'gloryofrobots'
import math
from obin.types import api, space
from obin.misc.platform import rarithmetic, rfloat
from obin.runtime import error

# TODO error here 2 % 0

# 15.7.3.2
w_MAX_VALUE = space.newnumber(1.7976931348623157e308)

# 15.7.3.3
w_MIN_VALUE = space.newnumber(5e-320)

# 15.7.3.4
w_NAN = space.newnumber(rfloat.NAN)

# 15.7.3.5
w_POSITIVE_INFINITY = space.newnumber(rfloat.INFINITY)

# 15.7.3.6
w_NEGATIVE_INFINITY = space.newnumber(-rfloat.INFINITY)

def add_i_i(l, r):
    ileft = api.to_i(l)
    iright = api.to_i(r)
    try:
        return space.newint(rarithmetic.ovfcheck(ileft + iright))
    except OverflowError:
        return space.newfloat(float(ileft) + float(iright))


def add_f_f(l, r):
    fleft = api.to_f(l)
    fright = api.to_f(r)
    return space.newfloat(fleft + fright)


def add_n_n(lprim, rprim):
    if space.isint(lprim) and space.isint(rprim):
        return add_i_i(lprim, rprim)
    else:
        return add_f_f(lprim, rprim)


def sub_i_i(nleft, nright):
    ileft = api.to_i(nleft)
    iright = api.to_i(nright)
    try:
        return space.newint(rarithmetic.ovfcheck(ileft - iright))
    except OverflowError:
        return space.newfloat(float(ileft) - float(iright))


def sub_f_f(nleft, nright):
    fleft = api.to_f(nleft)
    fright = api.to_f(nright)
    return space.newfloat(fleft - fright)


def sub_n_n(nleft, nright):
    if space.isint(nleft) and space.isint(nright):
        return sub_i_i(nleft, nright)
    return sub_f_f(nleft, nright)


def mult_f_f(nleft, nright):
    fleft = api.to_f(nleft)
    fright = api.to_f(nright)
    return space.newfloat(fleft * fright)


def mult_i_i(nleft, nright):
    ileft = api.to_i(nleft)
    iright = api.to_i(nright)
    try:
        return space.newint(rarithmetic.ovfcheck(ileft * iright))
    except OverflowError:
        return space.newfloat(float(ileft) * float(iright))


def mult_n_n(nleft, nright):
    if space.isint(nleft) and space.isint(nright):
        return mult_i_i(nleft, nright)
    return mult_f_f(nleft, nright)


def div_i_i(nleft, nright):
    ileft = api.to_i(nleft)
    iright = api.to_i(nright)
    try:
        z = rarithmetic.ovfcheck(ileft // iright)
    except ZeroDivisionError:
        return error.throw_2(error.Errors.ZERO_DIVISION_ERROR, nleft, nright)
    except OverflowError:
        return space.newfloat(float(ileft // iright))

    return space.newint(z)


def div_f_f(nleft, nright):
    # TODO EXCEPTIONS
    fleft = api.to_f(nleft)
    fright = api.to_f(nright)

    if rfloat.isnan(fleft) or rfloat.isnan(fright):
        return w_NAN

    if rfloat.isinf(fleft) and rfloat.isinf(fright):
        return w_NAN

    if rfloat.isinf(fright):
        return space.newfloat(0.0)

    try:
        val = fleft / fright
    except ZeroDivisionError:
        return error.throw_2(error.Errors.ZERO_DIVISION_ERROR, nleft, nright)

    return space.newfloat(val)


def div_n_n(nleft, nright):
    if space.isint(nleft) and space.isint(nright):
        return div_i_i(nleft, nright)

    return div_f_f(nleft, nright)


def mod_f_f(nleft, nright):
    fleft = api.to_f(nleft)
    fright = api.to_f(nright)

    if rfloat.isnan(fleft) or rfloat.isnan(fright):
        return w_NAN

    if rfloat.isinf(fright) or fright == 0:
        return w_NAN

    if rfloat.isinf(fright):
        return nleft

    if fleft == 0:
        return nleft

    return space.newfloat(math.fmod(fleft, fright))


def mod_n_n(nleft, nright):
    return mod_f_f(nleft, nright)


def uminus_f(obj):
    n1 = api.to_f(obj)
    return space.newfloat(-n1)


def uminus_i(obj):
    intval = api.to_i(obj)
    if intval == 0:
        return space.newfloat(-float(intval))
    return space.newint(-intval)


def uminus_n(obj):
    if space.isint(obj):
        return uminus_i(obj)
    return uminus_f(obj)


def compare_gt_i_i(w_x, w_y):
    x = api.to_i(w_x)
    y = api.to_i(w_y)
    return space.newbool(x > y)


def compare_gt_f_f(w_x, w_y):
    x = api.to_f(w_x)
    y = api.to_f(w_y)
    return space.newbool(x > y)


def compare_gt_n_n(x, y):
    if space.isint(x) and space.isint(y):
        return compare_gt_i_i(x, y)

    return compare_gt_f_f(x, y)


def compare_ge_i_i(w_x, w_y):
    x = api.to_i(w_x)
    y = api.to_i(w_y)
    return space.newbool(x >= y)


def compare_ge_f_f(w_x, w_y):
    x = api.to_f(w_x)
    y = api.to_f(w_y)
    return space.newbool(x >= y)


def compare_ge_n_n(x, y):
    if space.isint(x) and space.isint(y):
        return compare_ge_i_i(x, y)
    return compare_ge_f_f(x, y)


def compare_lt_i_i(w_x, w_y):
    return compare_gt_i_i(w_y, w_x)


def compare_lt_f_f(w_x, w_y):
    return compare_gt_f_f(w_y, w_x)


def compare_lt_n_n(w_x, w_y):
    return compare_gt_n_n(w_y, w_x)


def compare_le_i_i(w_x, w_y):
    return compare_ge_i_i(w_y, w_x)


def compare_le_f_f(w_x, w_y):
    return compare_ge_f_f(w_y, w_x)


def compare_le_n_n(w_x, w_y):
    return compare_ge_n_n(w_y, w_x)


def bitand_i_i(op1_w, op2_w):
    op1 = api.to_i(op1_w)
    op2 = api.to_i(op2_w)
    return space.newint(int(op1 & op2))


def bitxor_i_i(op1_w, op2_w):
    op1 = api.to_i(op1_w)
    op2 = api.to_i(op2_w)
    return space.newint(int(op1 ^ op2))


def bitor_i_i(op1_w, op2_w):
    op1 = api.to_i(op1_w)
    op2 = api.to_i(op2_w)
    return space.newint(int(op1 | op2))


def bitnot_i(op1_w):
    op = api.to_i(op1_w)
    return space.newint(~op)


def ursh_i_i(lval, rval):
    lnum = api.to_i(lval)
    rnum = api.to_i(rval)

    # from obin.misc.platform.rarithmetic import ovfcheck_float_to_int

    shift_count = rnum & 0x1F
    res = lnum >> shift_count
    return space.newnumber(res)


def rsh_i_i(lval, rval):
    lnum = api.to_i(lval)
    rnum = api.to_i(rval)

    # from obin.misc.platform.rarithmetic import ovfcheck_float_to_int

    # shift_count = rnum & 0x1F
    # res = lnum >> shift_count
    res = lnum >> rnum
    return space.newnumber(res)


def lsh_i_i(lval, rval):
    lnum = api.to_i(lval)
    rnum = api.to_i(rval)

    res = lnum << rnum
    # shift_count = rarithmetic.intmask(rnum & 0x1F)
    # res = lnum << shift_count

    return space.newnumber(res)


