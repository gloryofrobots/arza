from oroot import W_Cell
from ovalue import W_ValueType
from obin.runtime.exception import *
from osequence import W_SequenceIterator
from obin.utils.builtins import absent_index


class W_Vector(W_Cell):
    def __init__(self, items):
        W_Cell.__init__(self)
        assert isinstance(items, list)
        self._items = items

    def __iter__(self):
        for i in self._items:
            yield i

    # def __str__(self):
    #     return u'W_Vector("%s")' % str(self._items)

    def _put_(self, k, v):
        from obin.objects.space import isint
        from obin.objects import api
        assert isint(k)
        i = api.to_native_integer(k)
        try:
            self._items[i] = v
        except:
            raise ObinKeyError(k)

    def _traits_(self):
        from obin.objects.space import state
        return state.traits.VectorTraits

    def _clone_(self):
        items = []
        for v in self._items:
            items.append(v)
        return W_Vector(items)

    def _at_(self, index):
        from obin.objects.space import newundefined, isint
        from obin.objects import api
        assert isint(index)
        try:
            el = self._items[api.to_native_integer(index)]
        except ObinKeyError:
            return newundefined()

        return el

    def _iterator_(self):
        return W_SequenceIterator(self)

    def _tobool_(self):
        return bool(self._items)

    def _length_(self):
        return len(self._items)

    def _delete_(self, key):
        del self._items[key]

    def _tostring_(self):
        return str(self._items)

    def _at_index_(self, i):
        return self._items[i]

    def _put_at_index_(self, i, obj):
        try:
            self._items[i] = obj
        except:
            raise

    def _get_index_(self, obj):
        try:
            return self._items.index(obj)
        except ValueError:
            return absent_index()

    def ensure_size(self, size):
        assert size > 0
        l = self._length_()
        if size <= l:
            return

        self._items += [None] * (size - l)

    def append(self, v):
        from obin.objects.space import isany
        assert isany(v)
        self._items.append(v)

    def prepend(self, v):
        from obin.objects.space import isany
        assert isany(v)
        self._items.insert(0, v)

    def insert(self, index, v):
        from obin.objects.space import isany
        assert isany(v)
        self._items.insert(index, v)

    def remove(self, v):
        from obin.objects.space import isany
        assert isany(v)
        self._items.remove(v)

    def to_list(self):
        return self._items

    def append_many(self, items):
        self._items += items

    def pop(self):
        return self._items.pop()

    def concat(self, v):
        assert isinstance(v, W_Vector)
        self._items += v.to_list()

    def fold_slice_into_itself(self, index):
        assert index >= 0
        if index == 0:
            rest = self._clone_()
            self._items = [rest]
        else:
            rest = W_Vector(self._items[index:])
            self._items = self._items[0:index]
            self._items.append(rest)

    def append_value_multiple_times(self, val, times):
        assert times > 0
        self._items = self._items + [val] * times

    def exclude_index(self, idx):
        assert idx > 0
        items = self._items
        self._items = items[:idx] + items[idx + 1:]
