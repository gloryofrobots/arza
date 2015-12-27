from oroot import W_Hashable
from osequence import W_SequenceIterator
from obin.runtime.error import *
from obin.objects import api

"""
 @jit.look_inside_iff(lambda self, _1: _unroll_condition(self))
    def descr_hash(self, space):
        mult = 1000003
        x = 0x345678
        z = len(self.wrappeditems)
        for w_item in self.wrappeditems:
            y = space.hash_w(w_item)
            x = (x ^ y) * mult
            z -= 1
            mult += 82520 + z + z
        x += 97531
        return space.wrap(intmask(x))

    def descr_eq(self, space, w_other):
        if not isinstance(w_other, W_AbstractTupleObject):
            return space.w_NotImplemented
        return self._descr_eq(space, w_other)

    @jit.look_inside_iff(_unroll_condition_cmp)
    def _descr_eq(self, space, w_other):
        items1 = self.wrappeditems
        items2 = w_other.tolist()
        lgt1 = len(items1)
        lgt2 = len(items2)
        if lgt1 != lgt2:
            return space.w_False
        for i in range(lgt1):
            item1 = items1[i]
            item2 = items2[i]
            if not space.eq_w(item1, item2):
                return space.w_False
        return space.w_True
"""


class W_Tuple(W_Hashable):
    def __init__(self, items):
        assert isinstance(items, list)
        W_Hashable.__init__(self)
        self.elements = list(items)

    def __iter__(self):
        for v in self.elements:
            yield v

    def _compute_hash_(self):
        from rpython.rlib.rarithmetic import intmask
        x = 0x345678
        for item in self.elements:
            y = api.n_hash(item)
            x = intmask((1000003 * x) ^ y)
        return x

    def _traits_(self, process):
        return process.stdlib.traits.TupleTraits

    def _clone_(self):
        return W_Tuple(self.elements)

    def _at_(self, index):
        from obin.objects.space import newundefined, isint
        assert isint(index)
        try:
            el = self.elements[api.to_native_integer(index)]
        except ObinKeyError:
            return newundefined()

        return el

    def _at_index_(self, i):
        return self.elements[i]

    def _get_index_(self, obj):
        try:
            return self.elements.index(obj)
        except ValueError:
            return -1

    def _iterator_(self):
        return W_SequenceIterator(self)

    def _tobool_(self):
        return bool(self.elements)

    def _length_(self):
        return len(self.elements)

    def _tostring_(self):
        return "(%s,)" % ",".join([v._tostring_() for v in self.elements])


# def append(tupl, v):
#     items = tupl.values + [v]
#     return W_Tuple(items)
#
#
# def prepend(tupl, v):
#     items = [v] + tupl.values
#     return W_Tuple(items)
#
#
# def insert(tupl, index, v):
#     items = tupl.values
#     first = items[0:index]
#     second = items[index:]
#     items = first + [v] + second
#     return W_Tuple(items)
#
#
# def remove(tupl, v):
#     items = tupl.values
#     index = tupl.values.index(v)
#     first = items[0:index - 1]
#     second = items[index:]
#     items = first + second
#     return W_Tuple(items)
#
#
# def append_items(tupl, items):
#     items = tupl.values + items
#     return W_Tuple(items)
#
#
# def remove_last(tupl):
#     items = tupl.values[0:len(tupl.values) - 1]
#     return W_Tuple(items)
#
#
# def remove_first(tupl):
#     items = tupl.values[1:len(tupl.values)]
#     return W_Tuple(items)
#
#
# def concat(tupl, v):
#     tupl.values += v.values()
#
#
# def fold_slice(tupl, index):
#     items = tupl.values
#     slice = items[index:]
#     rest = items[0:index]
#     items = rest + [slice,]
#     return W_Tuple(items)
#
#
# def append_value_multiple_times(tupl, val, times):
#     tupl.values = tupl.values + [val] * times
