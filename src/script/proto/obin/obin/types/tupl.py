from obin.types.root import W_Hashable, W_Any
from sequence import W_SequenceIterator
from obin.runtime import error
from obin.types import api

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

    def _behavior_(self, process):
        return process.std.behaviors.Tuple

    def _clone_(self):
        return W_Tuple(self.elements)

    def _at_(self, index):
        from obin.types.space import newundefined, isint
        assert isint(index)
        try:
            el = self.elements[api.to_native_integer(index)]
        except KeyError:
            return newundefined()

        return el

    def _at_index_(self, i):
        return self.elements[i]

    def _slice_(self, start, end):
        from obin.types.space import isundefined
        from obin.types import api

        if isundefined(start):
            start_index = 0
        else:
            start_index = api.to_native_integer(start)

        if isundefined(end):
            end_index = self._length_()
        else:
            end_index = api.to_native_integer(end)

        elements = self.elements[start_index:end_index]
        return W_Tuple(elements)

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

    def _equal_(self, other):
        from obin.types import space
        if not space.istuple(other):
            return False

        if self._length_() != other._length_():
            return False

        for el1, el2 in zip(self.elements, other.elements):
            if not api.n_equal(el1, el2):
                return False

        return True

    def _tostring_(self):
        repr = ", ".join([v._tostring_() for v in self.elements])
        if self._length_() == 1:
            return "(%s,)" % repr
        return "(%s)" % repr

    def to_py_list(self):
        return self.elements


def concat(process, tupl1, tupl2):
    return W_Tuple(tupl1.elements + tupl2.elements)

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
