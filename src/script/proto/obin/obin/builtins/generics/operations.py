import math
from obin.types import api, space
from obin.misc.platform import rarithmetic, rfloat
from obin.runtime import error

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


def add_s_s(process, l, r):
    sleft = api.to_u(l)
    sright = api.to_u(r)
    return space.newstring(sleft + sright)


def add_i_i(process, l, r):
    ileft = api.to_i(l)
    iright = api.to_i(r)
    try:
        return space.newint(rarithmetic.ovfcheck(ileft + iright))
    except OverflowError:
        return space.newfloat(float(ileft) + float(iright))


def add_f_f(process, l, r):
    fleft = api.to_f(l)
    fright = api.to_f(r)
    return space.newfloat(fleft + fright)


def add_n_n(process, lprim, rprim):
    if space.isstring(lprim) or space.isstring(rprim):
        return add_s_s(process, lprim, rprim)

    if space.isint(lprim) and space.isint(rprim):
        return add_i_i(process, lprim, rprim)
    else:
        return add_f_f(process, lprim, rprim)


def sub_i_i(process, nleft, nright):
    ileft = api.to_i(nleft)
    iright = api.to_i(nright)
    try:
        return space.newint(rarithmetic.ovfcheck(ileft - iright))
    except OverflowError:
        return space.newfloat(float(ileft) - float(iright))


def sub_f_f(process, nleft, nright):
    fleft = api.to_f(nleft)
    fright = api.to_f(nright)
    return space.newfloat(fleft - fright)


def sub_n_n(process, nleft, nright):
    if space.isint(nleft) and space.isint(nright):
        return sub_i_i(process, nleft, nright)
    return sub_f_f(process, nleft, nright)


def mult_f_f(process, nleft, nright):
    fleft = api.to_f(nleft)
    fright = api.to_f(nright)
    return space.newfloat(fleft * fright)


def mult_i_i(process, nleft, nright):
    ileft = api.to_i(nleft)
    iright = api.to_i(nright)
    try:
        return space.newint(rarithmetic.ovfcheck(ileft * iright))
    except OverflowError:
        return space.newfloat(float(ileft) * float(iright))


def mult_n_n(process, nleft, nright):
    if space.isint(nleft) and space.isint(nright):
        return mult_i_i(process, nleft, nright)
    return mult_f_f(process, nleft, nright)


def div_i_i(process, nleft, nright):
    ileft = api.to_i(nleft)
    iright = api.to_i(nright)
    try:
        z = rarithmetic.ovfcheck(ileft // iright)
    except ZeroDivisionError:
        return error.throw_2(error.Errors.ZERO_DIVISION, nleft, nright)
    except OverflowError:
        return space.newfloat(float(ileft // iright))

    return space.newint(z)


def div_f_f(process, nleft, nright):
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
        return error.throw_2(error.Errors.ZERO_DIVISION, nleft, nright)

    return space.newfloat(val)


def div_n_n(process, nleft, nright):
    if space.isint(nleft) and space.isint(nright):
        return div_i_i(process, nleft, nright)

    return div_f_f(process, nleft, nright)


def mod_f_f(process, nleft, nright):
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


def mod_n_n(process, nleft, nright):
    return mod_f_f(process, nleft, nright)


def uminus_f(process, obj):
    n1 = api.to_f(obj)
    return space.newfloat(-n1)


def uminus_i(process, obj):
    intval = api.to_i(obj)
    if intval == 0:
        return space.newfloat(-float(intval))
    return space.newint(-intval)


def uminus_n(process, obj):
    if space.isint(obj):
        return uminus_i(process, obj)
    return uminus_f(process, obj)


def compare_gt_i_i(process, w_x, w_y):
    x = api.to_i(w_x)
    y = api.to_i(w_y)
    return space.newbool(x > y)


def compare_gt_f_f(process, w_x, w_y):
    x = api.to_f(w_x)
    y = api.to_f(w_y)
    return space.newbool(x > y)


def compare_gt_n_n(process, x, y):
    if space.isint(x) and space.isint(y):
        return compare_gt_i_i(process, x, y)

    return compare_gt_f_f(process, x, y)


def compare_ge_i_i(process, w_x, w_y):
    x = api.to_i(w_x)
    y = api.to_i(w_y)
    return space.newbool(x >= y)


def compare_ge_f_f(process, w_x, w_y):
    x = api.to_f(w_x)
    y = api.to_f(w_y)
    return space.newbool(x >= y)


def compare_ge_n_n(process, x, y):
    if space.isint(x) and space.isint(y):
        return compare_ge_i_i(process, x, y)
    return compare_ge_f_f(process, x, y)


def compare_lt_i_i(process, w_x, w_y):
    return compare_gt_i_i(process, w_y, w_x)


def compare_lt_f_f(process, w_x, w_y):
    return compare_gt_f_f(process, w_y, w_x)


def compare_lt_n_n(process, w_x, w_y):
    return compare_gt_n_n(process, w_y, w_x)


def compare_le_i_i(process, w_x, w_y):
    return compare_ge_i_i(process, w_y, w_x)


def compare_le_f_f(process, w_x, w_y):
    return compare_ge_f_f(process, w_y, w_x)


def compare_le_n_n(process, w_x, w_y):
    return compare_ge_n_n(process, w_y, w_x)


def in_w(process, left, right):
    return api.contains(right, left)


def notin_w(process, left, right):
    return space.newbool(not api.contains_b(right, left))


def bitand_i_i(process, op1_w, op2_w):
    op1 = api.to_i(op1_w)
    op2 = api.to_i(op2_w)
    return space.newint(int(op1 & op2))


def bitxor_i_i(process, op1_w, op2_w):
    op1 = api.to_i(op1_w)
    op2 = api.to_i(op2_w)
    return space.newint(int(op1 ^ op2))


def bitor_i_i(process, op1_w, op2_w):
    op1 = api.to_i(op1_w)
    op2 = api.to_i(op2_w)
    return space.newint(int(op1 | op2))


def bitnot_i(process, op1_w):
    op = api.to_i(op1_w)
    return space.newint(~op)


def ursh_i_i(process, lval, rval):
    lnum = api.to_i(lval)
    rnum = api.to_i(rval)

    # from obin.misc.platform.rarithmetic import ovfcheck_float_to_int

    shift_count = rnum & 0x1F
    res = lnum >> shift_count
    return space.newnumber(res)


def rsh_i_i(process, lval, rval):
    lnum = api.to_i(lval)
    rnum = api.to_i(rval)

    # from obin.misc.platform.rarithmetic import ovfcheck_float_to_int

    # shift_count = rnum & 0x1F
    # res = lnum >> shift_count
    res = lnum >> rnum
    return space.newnumber(res)


def lsh_i_i(process, lval, rval):
    lnum = api.to_i(lval)
    rnum = api.to_i(rval)

    res = lnum << rnum
    # shift_count = rarithmetic.intmask(rnum & 0x1F)
    # res = lnum << shift_count

    return space.newnumber(res)


def uplus_n(process, op1):
    return op1


def not_w(process, val):
    v = api.to_b(val)
    return space.newbool(not v)


def eq_w(process, op1, op2):
    return api.equal(op1, op2)


def str_w(process, op1):
    return api.to_string(op1)


def len_w(process, op1):
    return api.length(op1)


def list_v(process, op1):
    pass


def noteq_w(process, op1, op2):
    # TODO api.ne
    return space.newbool(not api.to_b(api.equal(op1, op2)))


def isnot_w_w(process, op1, op2):
    # TODO api.isnot
    return space.newbool(not api.to_b(api.strict_equal(op1, op2)))


def is_w_w(process, op1, op2):
    return api.strict_equal(op1, op2)


# TODO MAKE IT GENERIC
def cons_w(process, op1, op2):
    from obin.types.plist import plist1, cons
    from obin.types.space import islist
    if not islist(op2):
        l = plist1(op2)
    else:
        l = op2
    return cons(op1, l)


def isa_w_w(process, obj, trait):
    from obin.types import entity
    if space.islist(trait):
        if not space.isentity(obj):
            return entity.newentity_with_traits(process, obj, trait)
        return entity.add_traits(process, obj, trait)
    elif space.istrait(trait):
        if not space.isentity(obj):
            return entity.newentity_with_trait(process, obj, trait)
        return entity.add_trait(process, obj, trait)
    else:
        error.throw_2(error.Errors.TYPE, trait, space.newstring(u"expected trait or list of traits"))


def nota_w_w(process, obj, trait):
    from obin.types import entity
    if not space.isentity(obj):
        return error.throw_2(error.Errors.TYPE, obj, space.newstring(u"expected entity, got primitive type"))

    if space.islist(trait):
        return entity.remove_traits(process, obj, trait)
    elif space.istrait(trait):
        return entity.remove_trait(process, obj, trait)
    else:
        error.throw_2(error.Errors.TYPE, trait, space.newstring(u"expected trait or list of traits"))


def kindof_w_w(process, obj, trait):
    if space.islist(trait):
        return api.kindof_list(process, obj, trait)
    return api.kindof(process, obj, trait)


# TODO IMPLEMENT
def as_w_w(process, op1, op2):
    raise NotImplementedError()
