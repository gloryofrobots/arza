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


def add(lprim, rprim):
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


def sub(nleft, nright):
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


def mul(nleft, nright):
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


def div(nleft, nright):
    if space.isint(nleft) and space.isint(nright):
        return div_i_i(nleft, nright)

    return div_f_f(nleft, nright)


def mod_f_f(nleft, nright):
    fleft = api.to_f(nleft)
    fright = api.to_f(nright)

    if fright == 0:
        error.throw_2(error.Errors.ZERO_DIVISION_ERROR, nleft, nright)

    if rfloat.isnan(fleft) or rfloat.isnan(fright):
        return w_NAN

    if rfloat.isinf(fright):
        return w_NAN

    if fleft == 0:
        return nleft

    return space.newfloat(math.fmod(fleft, fright))


def mod(nleft, nright):
    return mod_f_f(nleft, nright)


def negate_f(obj):
    n1 = api.to_f(obj)
    return space.newfloat(-n1)


def negate_i(obj):
    intval = api.to_i(obj)
    if intval == 0:
        return space.newfloat(-float(intval))
    return space.newint(-intval)


def negate(obj):
    if space.isint(obj):
        return negate_i(obj)
    return negate_f(obj)


def gt_i_i(w_x, w_y):
    x = api.to_i(w_x)
    y = api.to_i(w_y)
    return space.newbool(x > y)


def gt_f_f(w_x, w_y):
    x = api.to_f(w_x)
    y = api.to_f(w_y)
    return space.newbool(x > y)


def gt(x, y):
    if space.isint(x) and space.isint(y):
        return gt_i_i(x, y)

    return gt_f_f(x, y)


def ge_i_i(w_x, w_y):
    x = api.to_i(w_x)
    y = api.to_i(w_y)
    return space.newbool(x >= y)


def ge_f_f(w_x, w_y):
    x = api.to_f(w_x)
    y = api.to_f(w_y)
    return space.newbool(x >= y)


def ge(x, y):
    if space.isint(x) and space.isint(y):
        return ge_i_i(x, y)
    return ge_f_f(x, y)


def lt_i_i(w_x, w_y):
    return gt_i_i(w_y, w_x)


def lt_f_f(w_x, w_y):
    return gt_f_f(w_y, w_x)


def lt(w_x, w_y):
    return gt(w_y, w_x)


def le_i_i(w_x, w_y):
    return ge_i_i(w_y, w_x)


def le_f_f(w_x, w_y):
    return ge_f_f(w_y, w_x)


def le(w_x, w_y):
    return ge(w_y, w_x)


def bitand(op1_w, op2_w):
    op1 = api.to_i(op1_w)
    op2 = api.to_i(op2_w)
    return space.newint(int(op1 & op2))


def bitxor(op1_w, op2_w):
    op1 = api.to_i(op1_w)
    op2 = api.to_i(op2_w)
    return space.newint(int(op1 ^ op2))


def bitor(op1_w, op2_w):
    op1 = api.to_i(op1_w)
    op2 = api.to_i(op2_w)
    return space.newint(int(op1 | op2))


def bitnot(op1_w):
    op = api.to_i(op1_w)
    return space.newint(~op)


def ursh(lval, rval):
    lnum = api.to_i(lval)
    rnum = api.to_i(rval)

    # from obin.misc.platform.rarithmetic import ovfcheck_float_to_int

    shift_count = rnum & 0x1F
    res = lnum >> shift_count
    return space.newnumber(res)


def rsh(lval, rval):
    lnum = api.to_i(lval)
    rnum = api.to_i(rval)

    # from obin.misc.platform.rarithmetic import ovfcheck_float_to_int

    # shift_count = rnum & 0x1F
    # res = lnum >> shift_count
    res = lnum >> rnum
    return space.newnumber(res)


def lsh(lval, rval):
    lnum = api.to_i(lval)
    rnum = api.to_i(rval)

    res = lnum << rnum
    # shift_count = rarithmetic.intmask(rnum & 0x1F)
    # res = lnum << shift_count

    return space.newnumber(res)


