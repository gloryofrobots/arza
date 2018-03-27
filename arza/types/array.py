from arza.types.root import W_Root
from arza.types import space, api
from arza.misc import platform
from arza.runtime import error


class W_Array(W_Root):
    def __init__(self, items):
        assert isinstance(items, list)
        self._items = items

    def __iter__(self):
        for i in self._items:
            yield i

    # def __str__(self):
    #     return u'W_Vector("%s")' % str(self._items)

    def _put_(self, k, v):
        from arza.types.space import isint
        from arza.types import api
        assert isint(k)
        i = api.to_i(k)
        try:
            self._items[i] = v
        except IndexError:
            return error.throw_2(error.Errors.INDEX_ERROR, space.newstring(u"Invalid index"))

        return self

    def _type_(self, process):
        return process.std.classes.Array

    def _clone_(self):
        items = []
        for v in self._items:
            items.append(v)
        return W_Array(items)

    def _at_(self, index):
        from arza.types.space import newvoid, isint
        from arza.types import api
        assert isint(index), (index.__class__.__name__, api.to_s(index))
        try:
            el = self._items[api.to_i(index)]
        except KeyError:
            return newvoid()

        return el

    def _length_(self):
        return len(self._items)

    def _equal_(self, other):
        if not space.isarray(other):
            return False

        if self._length_() != other._length_():
            return False

        for el1, el2 in zip(self._items, other._items):
            if not api.equal_b(el1, el2):
                return False

        return True

    def _to_string_(self):
        data = [v._to_string_() for v in self._items]
        repr = ", ".join(data)

        if self._length_() == 1:
            return "Array(%s,)" % repr
        return "Array(%s)" % repr

    def _to_repr_(self):
        return self._to_string_()

    def __repr__(self):
        return self._to_string_()

    def _delete_(self, key):
        del self._items[key]

    def _at_index_(self, i):
        return self._items[i]

    def _put_at_index_(self, i, obj):
        self._items[i] = obj
        return self

    def _get_index_(self, obj):
        try:
            return self._items.index(obj)
        except ValueError:
            return platform.absent_index()

    def to_l(self):
        return self._items


def type_check(t):
    error.affirm_type(t, space.isarray)


def empty():
    return W_Array([])


def ensure_size(arr, size):
    assert size > 0
    l = arr._length_()
    if size <= l:
        return

    arr._items += [None] * (size - l)
    return arr


def append(arr, v):
    from arza.types.space import isany
    assert isany(v)
    arr._items.append(v)
    return arr


def append_vector_items(arr, vec):
    from arza.types.space import isarray
    assert isarray(vec)
    arr.append_many(vec._items)
    return arr


def append_many(arr, items):
    arr._items += items
    return arr


def prepend(arr, v):
    from arza.types.space import isany
    assert isany(v)
    arr._items.insert(0, v)
    return arr


def insert(arr, index, v):
    from arza.types.space import isany
    assert isany(v)
    arr._items.insert(index, v)
    return arr


def remove(arr, v):
    from arza.types.space import isany
    assert isany(v)
    arr._items.remove(v)
    return arr


def pop(arr):
    return arr._items.pop()


def append_value_multiple_times(arr, val, times):
    assert times > 0
    arr._items = arr._items + [val] * times
    return arr


def exclude_index(arr, idx):
    assert idx >= 0
    items = arr._items
    arr._items = items[:idx] + items[idx + 1:]
    return arr


def concat(v1, v2):
    type_check(v1)
    type_check(v2)
    return W_Array(v1._items + v2._items)


def to_list(arr):
    type_check(arr)
    return space.newlist(arr._items)


def slice(arr, first, last):
    type_check(arr)
    assert isinstance(first, int)
    assert isinstance(last, int)
    if first < 0:
        error.throw_2(error.Errors.SLICE_ERROR, space.newstring(u"First index < 0"), space.newint(first))
    if first >= last:
        error.throw_3(error.Errors.SLICE_ERROR, space.newstring(u"First index >= Last index"),
                      space.newint(first), space.newint(last))
    if last >= arr.length:
        error.throw_2(error.Errors.SLICE_ERROR, space.newstring(u"Last index too big"), space.newint(last))
    return W_Array(arr._items[first:last])


def take(arr, count):
    type_check(arr)
    assert isinstance(count, int)
    if count < 0:
        error.throw_2(error.Errors.SLICE_ERROR, space.newstring(u"Count < 0"), space.newint(count))

    if count >= arr._length_():
        error.throw_2(error.Errors.SLICE_ERROR, space.newstring(u"Count too big"), space.newint(count))

    return W_Array(arr._items[:count])


def drop(arr, count):
    type_check(arr)
    assert isinstance(count, int)
    if count < 0:
        error.throw_2(error.Errors.SLICE_ERROR, space.newstring(u"Count < 0"), space.newint(count))

    if count >= arr._length_():
        error.throw_2(error.Errors.SLICE_ERROR, space.newstring(u"Count too big"), space.newint(count))

    return W_Array(arr._items[count:])
