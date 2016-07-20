__author__ = 'gloryofrobots'
from obin.types.number import *
from obin.runtime import error
from obin.types import api, space, plist, string, tuples, arguments
from obin.types.space import isnumber, isint, isdispatchable


class HotPath:
    def __init__(self, fn, arity):
        assert isinstance(arity, int)
        self.fn = fn
        self.arity = arity

    def apply(self, process, args):
        if api.length_i(args) != self.arity:
            return None
        return self.fn(process, args)


# TODO INLINE
def is_both_numbers(w1, w2):
    return isnumber(w1) and isnumber(w2)


def is_both_integers(w1, w2):
    return isint(w1) and isint(w2)


def is_both_strings(w1, w2):
    return space.isstring(w1) and space.isstring(w2)


# API#######################################################################

def hp_str(process, args):
    left = api.at_index(args, 0)
    if space.isatomictype(left):
        return api.to_string(left)
    else:
        return None


def hp_ne(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)
    if space.isatomictype(left):
        return api.not_equal(left, right)
    else:
        return None


def hp_eq(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)

    if space.isatomictype(left):
        return api.equal(left, right)
    else:
        return None


def hp_elem(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)

    if not isdispatchable(right):
        return api.contains(right, left)
    else:
        return None


def hp_put(process, args):
    key = api.at_index(args, 0)
    value = api.at_index(args, 1)
    obj = api.at_index(args, 2)
    # print "IN PUT", key, value, obj

    if not isdispatchable(obj):
        return api.put(obj, key, value)
    else:
        return None


def hp_at(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)

    if not isdispatchable(right):
        return api.at(right, left)
    else:
        return None


def hp_len(process, args):
    left = api.at_index(args, 0)

    if not isdispatchable(left):
        return api.length(left)
    else:
        return None


####NUMBERS##########################################################

def hp_add(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)

    if is_both_numbers(left, right):
        return add(left, right)
    else:
        return None


def hp_mod(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)

    if is_both_numbers(left, right):
        return mod(left, right)
    else:
        return None


def hp_mul(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)

    if is_both_numbers(left, right):
        return mul(left, right)
    else:
        return None


def hp_div(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)

    if is_both_numbers(left, right):
        return div(left, right)
    else:
        return None


def hp_sub(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)

    if is_both_numbers(left, right):
        return sub(left, right)
    else:
        return None


def hp_uminus(process, args):
    left = api.at_index(args, 0)

    if isnumber(left):
        return negate(left)
    else:
        return None


def hp_ge(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)
    if is_both_numbers(left, right):
        return ge(left, right)
    else:
        return None


def hp_gt(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)

    if is_both_numbers(left, right):
        return gt(left, right)
    else:
        return None


def hp_lt(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)

    if is_both_numbers(left, right):
        return gt(right, left)
    else:
        return None


def hp_le(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)
    if is_both_numbers(left, right):
        return ge(right, left)
    else:
        return None


############################################################
def hp_is_empty(process, args):
    left = api.at_index(args, 0)
    if not space.isdispatchable(left):
        return api.is_empty(left)
    else:
        return None


def hp_cons(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)
    if space.islist(right):
        res = plist.cons(left, right)
        # print "CONS", args, res
        return res
    else:
        return None


def hp_first(process, args):
    left = api.at_index(args, 0)
    if space.islist(left):
        return plist.head(left)
    else:
        return None


def hp_rest(process, args):
    left = api.at_index(args, 0)
    if space.islist(left):
        return plist.tail(left)
    else:
        return None


def hp_slice(process, args):
    obj = api.at_index(args, 2)
    if isdispatchable(obj):
        return None

    first = api.at_index(args, 0)
    last = api.at_index(args, 1)

    error.affirm_type(first, space.isint)
    error.affirm_type(last, space.isint)
    first_i = api.to_i(first)
    last_i = api.to_i(last)
    if space.islist(obj):
        return plist.slice(obj, first_i, last_i)
    elif space.istuple(obj):
        return tuples.slice(obj, first_i, last_i)
    elif space.isstring(obj):
        return string.slice(obj, first_i, last_i)
    else:
        return None


def hp_take(process, args):
    count = api.at_index(args, 0)

    obj = api.at_index(args, 1)
    if isdispatchable(obj):
        return None

    error.affirm_type(count, space.isint)
    count_i = api.to_i(count)

    if space.islist(obj):
        return plist.take(obj, count_i)
    elif space.isarguments(obj):
        return arguments.drop(obj, count_i)
    elif space.istuple(obj):
        return tuples.take(obj, count_i)
    elif space.isstring(obj):
        return string.take(obj, count_i)
    else:
        return None


def hp_drop(process, args):
    count = api.at_index(args, 0)

    obj = api.at_index(args, 1)
    if isdispatchable(obj):
        return None

    error.affirm_type(count, space.isint)
    count_i = api.to_i(count)

    if space.istuple(obj):
        return tuples.drop(obj, count_i)
    elif space.isarguments(obj):
        return arguments.drop(obj, count_i)
    elif space.islist(obj):
        return plist.drop(obj, count_i)
    elif space.isstring(obj):
        return string.drop(obj, count_i)
    else:
        return None


def hp_concat(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)
    if space.islist(right) and space.islist(left):
        return plist.concat(left, right)
    elif space.isstring(right) and space.isstring(left):
        return string.concat(left, right)
    else:
        return None