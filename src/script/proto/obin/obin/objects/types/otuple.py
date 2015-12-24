from oroot import W_Hashable
from ovalue import W_ValueType
from obin.runtime.exception import *
from obin.objects import api


class TupleIterator(W_ValueType):
    def __init__(self, source, length):
        assert isinstance(source, W_Tuple)
        assert isinstance(length, int)
        self.index = 0
        self.source = source
        self.tuple_length = length

    def _next_(self):
        from obin.objects.space import newundefined
        if self.index >= self.tuple_length:
            return newundefined()

        el = at(self.source, self.index)
        self.index += 1
        return el

    def _tostring_(self):
        return "<Iterator %d:%d>" % (self.index, self.tuple_length)

    def _tobool_(self):
        if self.index >= self.tuple_length:
            return False
        return True


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

    def _traits_(self):
        from obin.objects.space import state
        return state.traits.TupleTraits

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

    def _iterator_(self):
        return TupleIterator(self, self._length_())

    def _tobool_(self):
        return bool(self.elements)

    def _length_(self):
        return len(self.elements)

    def _tostring_(self):
        return "(%s,)" % ",".join([v._tostring_() for v in self.elements])


def at(tupl, i):
    return tupl.elements[i]


def has_index(tupl, i):
    return i > 0 and i < tupl._length_()


def get_index(tupl, obj):
    try:
        return tupl.elements.index(obj)
    except ValueError:
        return -1

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