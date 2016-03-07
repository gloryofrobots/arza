__author__ = 'gloryofrobots'
from obin.types.number import *
from obin.runtime import error
from obin.types import api, space, plist, string
from obin.types.space import isnumber, isint, isrecord


class HotPath:
    def __init__(self, fn, arity):
        assert isinstance(arity, int)
        self.fn = fn
        self.arity = arity

    def apply(self, process, args):
        if api.length_i(args) != self.arity:
            return None
        if not self.fn:
            print "OLOO"
        return self.fn(process, args)


# TODO INLINE
def is_both_numbers(w1, w2):
    return isnumber(w1) and isnumber(w2)


def is_both_integers(w1, w2):
    return isint(w1) and isint(w2)


def is_both_strings(w1, w2):
    return space.isstring(w1) and space.isstring(w2)


def is_not_records(w1, w2):
    return (not isrecord(w1)) and (not isrecord(w2))


# API#######################################################################
def hp_ne(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)
    if is_not_records(left, right):
        return api.not_equal(left, right)
    else:
        return None


def hp_eq(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)

    if is_not_records(left, right):
        return api.equal(left, right)
    else:
        return None


def hp_contains(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)

    if is_not_records(left, right):
        return api.contains(left, right)
    else:
        return None


####NUMBERS##########################################################

def hp_add(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)

    if is_both_numbers(left, right):
        return add_n_n(left, right)
    else:
        return None


def hp_mod(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)

    if is_both_numbers(left, right):
        return mod_n_n(left, right)
    else:
        return None


def hp_mul(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)

    if is_both_numbers(left, right):
        return mult_n_n(left, right)
    else:
        return None


def hp_div(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)

    if is_both_numbers(left, right):
        return div_n_n(left, right)
    else:
        return None


def hp_sub(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)

    if is_both_numbers(left, right):
        return sub_n_n(left, right)
    else:
        return None


def hp_uminus(process, args):
    left = api.at_index(args, 0)

    if isnumber(left):
        return uminus_n(left)
    else:
        return None


def hp_ge(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)
    if is_both_numbers(left, right):
        return compare_ge_n_n(left, right)
    else:
        return None


def hp_gt(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)

    if is_both_numbers(left, right):
        return compare_gt_n_n(left, right)
    else:
        return None


def hp_lt(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)

    if is_both_numbers(left, right):
        return compare_gt_n_n(right, left)
    else:
        return None


def hp_le(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)
    if is_both_numbers(left, right):
        return compare_ge_n_n(right, left)
    else:
        return None


############################################################

def hp_cons(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)
    if space.islist(right):
        return plist.cons(left, right)
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

def hp_concat(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)
    if space.islist(right) and space.islist(left):
        return plist.concat(left, right)
    elif space.isstring(right) and space.isstring(left):
        return string.concat(left, right)
    else:
        return None
