__author__ = 'gloryofrobots'
from obin.builtins.generics.operations import *
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


def apply_binary(process, operation, left, right):
    return operation(process, left, right)


def apply_unary(process, operation, val):
    return operation(process, val)


def hp_as_(process, args):
    raise NotImplementedError()


def hp_is_(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)
    return apply_binary(process, is_w_w, left, right)


def hp_ne(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)
    if is_not_entities(left, right):
        return apply_binary(process, noteq_w, left, right)
    else:
        return None


def hp_eq(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)

    if is_not_entities(left, right):
        return apply_binary(process, eq_w, left, right)
    else:
        return None


def hp_not_(process, args):
    left = api.at_index(args, 0)
    if not space.isentity(left):
        return apply_unary(process, not_w, left)
    else:
        return None


def hp_isnot(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)
    if is_not_entities(left, right):
        return apply_binary(process, isnot_w_w, left, right)
    else:
        return None


def hp_in_(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)

    if is_not_entities(left, right):
        return apply_binary(process, in_w, left, right)
    else:
        return None


def hp_add(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)

    if is_both_numbers(left, right):
        return apply_binary(process, add_n_n, left, right)
    else:
        return None


def hp_append(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)

    if is_both_strings(left, right):
        return apply_binary(process, add_s_s, left, right)
    else:
        return None


def hp_mod(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)

    if is_both_numbers(left, right):
        return apply_binary(process, mod_n_n, left, right)
    else:
        return None


def hp_mul(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)

    if is_both_numbers(left, right):
        return mult_n_n(process, left, right)
    else:
        return None


def hp_div(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)

    if is_both_numbers(left, right):
        return apply_binary(process, div_n_n, left, right)
    else:
        return None


def hp_sub(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)

    if is_both_numbers(left, right):
        return apply_binary(process, sub_n_n, left, right)
    else:
        return None


def hp_uminus(process, args):
    left = api.at_index(args, 0)

    if isnumber(left):
        return apply_unary(process, uminus_n, left)
    else:
        return None


def hp_uplus(process, args):
    left = api.at_index(args, 0)
    if isnumber(left):
        return apply_unary(process, uplus_n, left)
    else:
        return None


def hp_ge(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)
    if is_both_numbers(left, right):
        return apply_binary(process, compare_ge_n_n, left, right)
    else:
        return None


def hp_gt(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)

    if is_both_numbers(left, right):
        return apply_binary(process, compare_gt_n_n, left, right)
    else:
        return None


def hp_lt(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)

    if is_both_numbers(left, right):
        return apply_binary(process, compare_gt_n_n, right, left)
    else:
        return None


def hp_le(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)
    if is_both_numbers(left, right):
        return apply_binary(process, compare_ge_n_n, right, left)
    else:
        return None


def hp_bitnot(process, args):
    left = api.at_index(args, 0)
    if isint(left):
        return apply_unary(process, bitnot_i, left)
    else:
        return None


def hp_bitor(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)

    if is_both_integers(left, right):
        return apply_binary(process, bitor_i_i, left, right)
    else:
        return None


def hp_bitxor(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)

    if is_both_integers(left, right):
        return apply_binary(process, bitxor_i_i, left, right)
    else:
        return None


def hp_bitand(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)

    if is_both_integers(left, right):
        return apply_binary(process, bitand_i_i, left, right)
    else:
        return None


def hp_lsh(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)

    if is_both_integers(left, right):
        return apply_binary(process, lsh_i_i, left, right)
    else:
        return None


def hp_rsh(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)

    if is_both_integers(left, right):
        return apply_binary(process, rsh_i_i, left, right)
    else:
        return None


def hp_ursh(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)
    if is_both_integers(left, right):
        return apply_binary(process, ursh_i_i, left, right)
    else:
        return None

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


def hp_notin(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)

    if is_not_entities(left, right):
        return apply_binary(process, notin_w, left, right)
    else:
        return None


def hp_nota(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)
    return apply_binary(process, nota_w_w, left, right)


def hp_isa(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)
    return apply_binary(process, isa_w_w, left, right)


def hp_kindof(process, args):
    left = api.at_index(args, 0)
    right = api.at_index(args, 1)
    return apply_binary(process, kindof_w_w, left, right)


def hp_str(process, args):
    return None


def hp_list(process, args):
    return None


def hp_len(process, args):
    return None
