from obin.types.root import W_Root
from obin.misc import platform
from obin.runtime import error



class W_Vector(W_Root):
    def __init__(self, items):
        assert isinstance(items, list)
        self._items = items

    def __iter__(self):
        for i in self._items:
            yield i

    # def __str__(self):
    #     return u'W_Vector("%s")' % str(self._items)

    def _put_(self, k, v):
        from obin.types.space import isint
        from obin.types import api
        assert isint(k)
        i = api.to_i(k)
        try:
            self._items[i] = v
            return True
        except IndexError:
            return False

    def _type_(self, process):
        return process.std.types.Vector

    def _clone_(self):
        items = []
        for v in self._items:
            items.append(v)
        return W_Vector(items)

    def _at_(self, index):
        from obin.types.space import newvoid, isint
        from obin.types import api
        assert isint(index)
        try:
            el = self._items[api.to_i(index)]
        except KeyError:
            return newvoid()

        return el

    def _length_(self):
        return len(self._items)

    def _delete_(self, key):
        del self._items[key]

    def _to_string_(self):
        return str(self._items)

    def _at_index_(self, i):
        return self._items[i]

    def _put_at_index_(self, i, obj):
        self._items[i] = obj

    def _get_index_(self, obj):
        try:
            return self._items.index(obj)
        except ValueError:
            return platform.absent_index()

    def ensure_size(self, size):
        assert size > 0
        l = self._length_()
        if size <= l:
            return

        self._items += [None] * (size - l)

    def append(self, v):
        from obin.types.space import isany
        assert isany(v)
        self._items.append(v)

    def append_vector_items(self, vec):
        from obin.types.space import isvector
        assert isvector(vec)
        self.append_many(vec._items)

    def append_many(self, items):
        self._items += items

    def prepend(self, v):
        from obin.types.space import isany
        assert isany(v)
        self._items.insert(0, v)

    def insert(self, index, v):
        from obin.types.space import isany
        assert isany(v)
        self._items.insert(index, v)

    def remove(self, v):
        from obin.types.space import isany
        assert isany(v)
        self._items.remove(v)

    def to_l(self):
        return self._items

    def pop(self):
        return self._items.pop()

    def append_value_multiple_times(self, val, times):
        assert times > 0
        self._items = self._items + [val] * times

    def exclude_index(self, idx):
        assert idx >= 0
        items = self._items
        self._items = items[:idx] + items[idx + 1:]


def concat(process, v1, v2):
    return W_Vector(v1._items + v2._items)
