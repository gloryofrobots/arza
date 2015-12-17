from root import W_Cell
from value import NativeListIterator
from obin.runtime.exception import *


class W_Tuple(W_Cell):
    _type_ = 'Tuple'

    def __init__(self, items):
        super(W_Tuple, self).__init__()
        assert isinstance(items, tuple)
        self.values = items

    def __iter__(self):
        return self.values.__iter__()

    def __hash__(self):
        return hash(self.values)

    def __str__(self):
        return str(self.values)

    def _traits_(self):
        from obin.objects.space import state
        return state.traits.TupleTraits

    def _clone_(self):
        return W_Tuple(self.values)

    def _at_(self, index):
        from obin.objects.space import newundefined, isint
        assert isint(index)
        try:
            el = self.values[index.value()]
        except ObinKeyError:
            return newundefined()

        return el

    def _iterator_(self):
        return NativeListIterator(self.values, self.length())

    def _tobool_(self):
        return bool(self.values)

    def _length_(self):
        return self.length()

    def _tostring_(self):
        return str(self.values)

    def at(self, i):
        return self.values[i]

    def has_index(self, i):
        return i > 0 and i < self.length()

    def get_index(self, obj):
        try:
            return self.values.index(obj)
        except ValueError:
            return -1

    def has(self, obj):
        return obj in self.values

    def length(self):
        return len(self.values)


def append(tupl, v):
    items = tupl.values + (v,)
    return W_Tuple(items)


def prepend(tupl, v):
    items = (v,) + tupl.values
    return W_Tuple(items)


def insert(tupl, index, v):
    items = tupl.values
    first = items[0:index]
    second = items[index:]
    items = first + (v,) + second
    return W_Tuple(items)


def remove(tupl, v):
    items = tupl.values
    index = tupl.values.index(v)
    first = items[0:index - 1]
    second = items[index:]
    items = first + second
    return W_Tuple(items)


def append_tuple(tupl, items):
    items = tupl.values + items
    return W_Tuple(items)


def remove_last(tupl):
    items = tupl.values[0:len(tupl.values) - 1]
    return W_Tuple(items)


def remove_first(tupl):
    items = tupl.values[1:len(tupl.values)]
    return W_Tuple(items)


def concat(tupl, v):
    tupl.values += v.values()


def fold_slice(tupl, index):
    items = tupl.values
    slice = items[index:]
    rest = items[0:index]
    items = rest + (slice,)
    return W_Tuple(items)


def append_value_multiple_times(tupl, val, times):
    tupl.values = tupl.values + [val] * times
