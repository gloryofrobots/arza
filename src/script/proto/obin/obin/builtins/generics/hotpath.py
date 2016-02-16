__author__ = 'gloryofrobots'
from obin.builtins.generics.operations import *
from obin.types.number import *
from obin.runtime import error
from obin.types import api, space, plist, string
from obin.types.space import isnumber, isint, isentity


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


def is_not_entities(w1, w2):
    return (not isentity(w1)) and (not isentity(w2))



# API#######################################################################
def hp_ne(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)
    if is_not_entities(left, right):
        return api.not_equal(left, right)
    else:
        return None


def hp_eq(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)

    if is_not_entities(left, right):
        return api.equal(left, right)
    else:
        return None


def hp_not_(process, args):
    left = api.at_index(args, 0)
    if not space.isentity(left):
        return api.not_(left)
    else:
        return None



def hp_in_(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)

    if is_not_entities(left, right):
        return api.in_(left, right)
    else:
        return None

def hp_notin(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)

    if is_not_entities(left, right):
        return api.notin(left, right)
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
        return  uminus_n(left)
    else:
        return None


def hp_uplus(process, args):
    left = api.at_index(args, 0)
    if isnumber(left):
        return uplus_n(left)
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


def hp_bitnot(process, args):
    left = api.at_index(args, 0)
    if isint(left):
        return  bitnot_i(left)
    else:
        return None


def hp_bitor(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)

    if is_both_integers(left, right):
        return bitor_i_i(left, right)
    else:
        return None


def hp_bitxor(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)

    if is_both_integers(left, right):
        return bitxor_i_i(left, right)
    else:
        return None


def hp_bitand(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)

    if is_both_integers(left, right):
        return bitand_i_i(left, right)
    else:
        return None


def hp_lsh(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)

    if is_both_integers(left, right):
        return lsh_i_i(left, right)
    else:
        return None


def hp_rsh(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)

    if is_both_integers(left, right):
        return rsh_i_i(left, right)
    else:
        return None


def hp_ursh(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)
    if is_both_integers(left, right):
        return ursh_i_i(left, right)
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


def hp_concat(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)
    if space.islist(right) and space.islist(left):
        return plist.concat(left, right)
    elif space.isstring(right) and space.isstring(left):
        return string.concat(left, right)
    else:
        return None




