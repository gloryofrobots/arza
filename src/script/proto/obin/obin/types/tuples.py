from obin.types.root import W_Hashable, W_Any
from sequence import W_SequenceIterator
from obin.runtime import error
from obin.types import api, space
from obin.misc import platform

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

class W_Unit(W_Any):
    def _hash_(self):
        return 0x345678

    def _clone_(self):
        return self

    def __iter__(self):
        raise StopIteration()

    def __getitem__(self, item):
        raise RuntimeError("Unit has no elements")

    def _type_(self, process):
        return process.std.types.Tuple

    def _contains_(self, key):
        return False

    def _at_(self, index):
        return space.newvoid()

    def _at_index_(self, i):
        return space.newvoid()

    def _slice_(self, start, end):
        return space.newvoid()

    def _get_index_(self, obj):
        return platform.absent_index()

    def _iterator_(self):
        return self

    def _length_(self):
        return 0

    def _equal_(self, other):
        if isinstance(other, W_Unit):
            return True
        return False

    def _to_string_(self):
        return "()"

    def to_l(self):
        return []


class W_Tuple(W_Hashable):
    def __init__(self, items):
        assert isinstance(items, list)
        W_Hashable.__init__(self)
        self.elements = items

    def __iter__(self):
        for v in self.elements:
            yield v

    def __getitem__(self, item):
        return self.elements[item]

    def __getslice__(self, start, end):
        return W_Tuple(self.elements[start:end])

    def _compute_hash_(self):
        from obin.misc.platform import rarithmetic
        x = 0x345678
        for item in self.elements:
            y = api.hash_i(item)
            x = rarithmetic.intmask((1000003 * x) ^ y)
        return x

    def _type_(self, process):
        return process.std.types.Tuple

    def _clone_(self):
        return W_Tuple(self.elements)

    def _contains_(self, key):
        for item in self.elements:
            if api.equal_b(item, key):
                return True
        return False

    def _at_(self, index):
        from obin.types.space import newvoid, isint
        assert isint(index)
        try:
            el = self.elements[api.to_i(index)]
        except IndexError:
            return newvoid()

        return el

    def _at_index_(self, i):
        return self.elements[i]

    def _slice_(self, start, end):

        if space.isvoid(start):
            start_index = 0
        else:
            start_index = api.to_i(start)

        if space.isvoid(end):
            end_index = self._length_()
        else:
            end_index = api.to_i(end)

        if start_index < 0:
            return space.newvoid()

        if end_index <= 0:
            return space.newvoid()

        elements = self.elements[start_index:end_index]
        return W_Tuple(elements)

    def _get_index_(self, obj):
        try:
            return self.elements.index(obj)
        except ValueError:
            return -1

    def _iterator_(self):
        return W_SequenceIterator(self)

    def _length_(self):
        return len(self.elements)

    def _equal_(self, other):
        from obin.types import space
        if not space.istuple(other):
            return False

        if self._length_() != other._length_():
            return False

        for el1, el2 in zip(self.elements, other.elements):
            if not api.equal_b(el1, el2):
                return False

        return True

    def _to_string_(self):
        repr = ", ".join([v._to_string_() for v in self.elements])

        if self._length_() == 1:
            return "(%s,)" % repr
        return "(%s)" % repr

    def to_l(self):
        return self.elements

def type_check(t):
    error.affirm_type(t, space.istuple)


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
