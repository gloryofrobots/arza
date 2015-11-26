
""" Base operations implementations
"""

import math

from obin.objects.object import W_String, W_Integer, W_Float
from obin.objects.object_space import _w, isint, isstring, isfloat, newbool
from rpython.rlib.rarithmetic import ovfcheck
from rpython.rlib.rfloat import isnan, isinf
from rpython.rlib.objectmodel import specialize
from obin.builtins.number_builtins import w_NAN, w_POSITIVE_INFINITY, w_NEGATIVE_INFINITY
from obin.objects import api

# 11.6.1, 11.6.3
def plus(r, lval, rval):
    lprim = lval
    rprim = rval

    if isinstance(lprim, W_String) or isinstance(rprim, W_String):
        sleft = api.tostring(lprim)
        sright = api.tostring(rprim)
        return W_String(sleft + sright)
    # hot path
    if isint(lprim) and isint(rprim):
        ileft = lprim.value()
        iright = rprim.value()
        try:
            return W_Integer(ovfcheck(ileft + iright))
        except OverflowError:
            return W_Float(float(ileft) + float(iright))
    else:
        fleft = lprim.value()
        fright = rprim.value()
        return W_Float(fleft + fright)

def sub(ctx, nleft, nright):
    if isint(nleft) and isint(nright):
        # XXX fff
        ileft = nleft.value()
        iright = nright.value()
        try:
            return W_Integer(ovfcheck(ileft - iright))
        except OverflowError:
            return W_Float(float(ileft) - float(iright))
    fleft = nleft.value()
    fright = nright.value()
    return W_Float(fleft - fright)


def mult(ctx, nleft, nright):
    if isint(nleft) and isint(nright):
        # XXXX test & stuff
        ileft = nleft.value()
        iright = nright.value()
        try:
            return W_Integer(ovfcheck(ileft * iright))
        except OverflowError:
            return W_Float(float(ileft) * float(iright))
    fleft = nleft.value()
    fright = nright.value()
    return W_Float(fleft * fright)


def mod(ctx, w_left, w_right):
    left = w_left.value()
    right = w_right.value()

    if isnan(left) or isnan(right):
        return w_NAN

    if isinf(left) or right == 0:
        return w_NAN

    if isinf(right):
        return w_left

    if left == 0:
        return w_left

    return W_Float(math.fmod(left, right))


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
def division(ctx, nleft, nright):
    fleft = nleft.value()
    fright = nright.value()
    if isnan(fleft) or isnan(fright):
        return w_NAN

    if isinf(fleft) and isinf(fright):
        return w_NAN

    if isinf(fleft) and fright == 0:
        s = sign_of(fleft, fright)
        return w_signed_inf(s)

    if isinf(fright):
        return _w(0)

    if fleft == 0 and fright == 0:
        return w_NAN

    if fright == 0:
        s = sign_of(fleft, fright)
        return w_signed_inf(s)

    val = fleft / fright
    return W_Float(val)


@specialize.argtype(0, 1)
def _compare_gt(x, y):
    return x > y


@specialize.argtype(0, 1)
def _compare_ge(x, y):
    return x >= y


def _base_compare(x, y, _compare):
    if isint(x) and isint(y):
        return _compare(x.value(), y.value())

    if isfloat(x) and isfloat(y):
        n1 = x.value()
        n2 = x.value()
        return _compare(n1, n2)

    if not (isstring(x) and isstring(y)):
        n1 = x.value()
        n2 = y.value()
        return _compare(n1, n2)
    else:
        s1 = x._tostring_()
        s2 = y._tostring_()
        return _compare(s1, s2)


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
        intval = obj.value()
        if intval == 0:
            return W_Float(-float(intval))
        return W_Integer(-intval)
    return W_Float(-obj.value())
