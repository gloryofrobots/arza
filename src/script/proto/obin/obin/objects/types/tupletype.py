from root import W_Cell
from value import W_ValueType
from obin.runtime.exception import *
from obin.objects import api

class TupleIterator(W_ValueType):
    def __init__(self, source, length):
        assert isinstance(source, W_Tuple)
        assert isinstance(length, int)
        self.index = 0
        self.source = source
        self.__source_length = length

    def _next_(self):
        from obin.objects.space import newundefined
        if self.index >= self.__source_length:
            return newundefined()

        el = self.source.at(self.index)
        self.index += 1
        return el

    def _tostring_(self):
        return "<Iterator %d:%d>" % (self.index, self.__source_length)

    def _tobool_(self):
        if self.index >= self.__source_length:
            return False
        return True

class W_Tuple(W_Cell):
    def __init__(self, items):
        W_Cell.__init__(self)
        assert isinstance(items, list)
        self.__values = list(items)

    def __iter__(self):
        for v in self.__values:
            yield v

    def __hash__(self):
        return hash(self.__values)

    def __str__(self):
        return "(%s,)" % ",".join([v._tostring_() for v in self.__values])

    def _traits_(self):
        from obin.objects.space import state
        return state.traits.TupleTraits

    def _clone_(self):
        return W_Tuple(self.__values)

    def _at_(self, index):
        from obin.objects.space import newundefined, isint
        assert isint(index)
        try:
            el = self.__values[api.to_native_integer(index)]
        except ObinKeyError:
            return newundefined()

        return el

    def _iterator_(self):
        return TupleIterator(self, self.length())

    def _tobool_(self):
        return bool(self.__values)

    def _length_(self):
        return self.length()

    def _tostring_(self):
        return str(self.__values)

    def at(self, i):
        return self.__values[i]

    def has_index(self, i):
        return i > 0 and i < self.length()

    def get_index(self, obj):
        try:
            return self.__values.index(obj)
        except ValueError:
            return -1

    def has(self, obj):
        return obj in self.__values

    def length(self):
        return len(self.__values)


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
