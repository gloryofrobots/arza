from obin.types.root import W_Any
from obin.types import space
from obin.types import api
from obin.runtime import error


class W_PList(W_Any):
    def __init__(self, head, tail):
        self.head = head
        self.tail = tail

    def __iter__(self):
        cur = self
        while not isempty(cur):
            yield head(cur)
            cur = cur.tail

    def __getitem__(self, index):
        assert isinstance(index, int)
        return nth(self, index)

    def __len__(self):
        return self._length_()

    def __getslice__(self, start, end):
        return slice(self, start, end)

    def show(self):
        els = []
        cur = self
        while True:
            if isempty(cur):
                els.append("()")
                break
            els.append("%s" % (cur.head))
            cur = cur.tail
        return str(els)

    def _tostring_(self):
        from obin.types import api
        els = []
        cur = self
        while True:
            if isempty(cur):
                break
            els.append(api.to_s(head(cur)))
            cur = cur.tail
        return "[%s]" % (", ".join(els))

    def _length_(self):
        return length(self)

    def _get_index_(self, obj):
        return index(self, obj)

    def _at_(self, key):
        from obin.types.space import newnil
        from obin.types import api
        int_index = api.to_i(key)
        if int_index < 0:
            return newnil()

        return nth(self, int_index)

    def _put_(self, k, v):
        from obin.types.space import isint
        from obin.types import api
        assert isint(k)
        i = api.to_i(k)
        return update(self, i, v)

    def _behavior_(self, process):
        return process.std.behaviors.List

    def _slice_(self, start, end):
        from obin.types.space import isnil, newnil
        from obin.types import api

        if isnil(start):
            start_index = 0
        else:
            start_index = api.to_i(start)

        # INTELLIGENT ERROR HERE, BECAUSE LISTS DON`T SUPPORT RELATIVE SLICING
        if start_index < 0:
            return newnil()

        if isnil(end):
            return drop(self, start_index)
        else:
            end_index = api.to_i(end)

        # INTELLIGENT ERROR HERE, BECAUSE LISTS DON`T SUPPORT RELATIVE SLICING
        if end_index < 0:
            return newnil()
        return slice(self, start_index, end_index)

    def _equal_(self, other):
        if not space.islist(other):
            return False

        if isempty(other) and isempty(self):
            return True
        return equal(self, other)


__EMPTY__ = W_PList(space.newnil(), space.newnil())


def empty():
    return __EMPTY__


def foldl(func, acc, pl):
    assert space.islist(pl)
    if isempty(pl):
        return acc

    return foldl(func,
                 func(acc, head(pl)),
                 tail(pl))


def foldr(func, acc, pl):
    assert space.islist(pl)
    if isempty(pl):
        return acc

    return func(head(pl),
                foldr(func, acc, tail(pl)))


def isempty(pl):
    return pl is __EMPTY__


def head(pl):
    assert space.islist(pl)
    return pl.head


def tail(pl):
    assert space.islist(pl)
    return pl.tail


def split(pl):
    assert space.islist(pl)
    return head(pl), tail(pl)


def _length_foldl(acc, el):
    return acc + 1


def length(pl):
    assert space.islist(pl)
    return foldl(_length_foldl, 0, pl)


def prepend(v, pl):
    assert space.islist(pl)
    assert v is not None
    return W_PList(v, pl)


def cons_n_list(items, pl):
    assert space.islist(pl)
    head = pl
    for item in reversed(items):
        head = prepend(item, head)
    return head


def append(pl, v):
    assert space.islist(pl)
    return insert(pl, length(pl), v)


def concat(pl1, pl2):
    assert space.islist(pl1)
    assert space.islist(pl2)
    return foldr(prepend, pl2, pl1)


def pop(pl):
    assert space.islist(pl)
    return pl.tail


def take(pl, count):
    assert space.islist(pl)
    if count <= 0:
        return empty()

    if isempty(pl):
        return error.throw_1(error.Errors.INDEX, space.newint(count))
    return prepend(head(pl), take(pop(pl), count - 1))


def drop(pl, count):
    assert space.islist(pl)
    if count == 0:
        return pl
    if isempty(pl):
        return error.throw_1(error.Errors.INDEX, space.newint(count))

    return drop(tail(pl), count - 1)


##############################################

def _slice(pl, index, start, end):
    if isempty(pl):
        return error.throw_3(error.Errors.SLICE, space.newint(index),
                             space.newint(start), space.newint(end))

    if index < start:
        return _slice(tail(pl), index + 1, start, end)

    if index < end:
        return prepend(head(pl), _slice(tail(pl), index + 1, start, end))

    return empty()


def slice(pl, start, end):
    assert space.islist(pl)
    if start == end:
        return empty()

    assert start >= 0
    assert end > start
    assert end > 0

    # return take(drop(pl, start), end - 1)
    return _slice(pl, 0, start, end)


##############################################

def _nth(pl, index):
    from obin.types.space import newnil
    if index == 0:
        return head(pl)
    if isempty(pl):
        return newnil()
    return nth(tail(pl), index - 1)


def nth(pl, index):
    assert space.islist(pl)
    assert index >= 0
    return _nth(pl, index)


def insert(pl, index, v):
    assert space.islist(pl)
    if index == 0:
        return prepend(v, pl)

    if isempty(pl):
        return error.throw_1(error.Errors.INDEX, space.newint(index))

    return W_PList(head(pl), insert(tail(pl), index - 1, v))


def update(pl, index, v):
    assert space.islist(pl)
    if index == 0:
        return prepend(v, tail(pl))

    if isempty(tail(pl)):
        return error.throw_1(error.Errors.INDEX, space.newint(index))

    return W_PList(head(pl), update(tail(pl), index - 1, v))


def remove_all(pl, v):
    assert space.islist(pl)
    if isempty(pl):
        return pl

    if api.n_equal(v, head(pl)):
        l = remove_all(tail(pl), v)
        return l
    l = W_PList(head(pl), remove_all(tail(pl), v))
    return l


def remove(pl, v):
    assert space.islist(pl)
    assert isinstance(pl, W_PList)
    from obin.types import api
    if isempty(pl):
        return error.throw_1(error.Errors.VALUE, space.newint(v))

    if api.n_equal(v, head(pl)):
        return tail(pl)

    return W_PList(head(pl), remove(tail(pl), v))


def contains_with(pl, v, condition):
    assert space.islist(pl)
    if isempty(pl):
        return False

    if condition(v, head(pl)):
        return True

    return contains_with(tail(pl), v, condition)


def contains(pl, v):
    return contains_with(pl, v, api.n_equal)


def contains_split(pl, v):
    assert space.islist(pl)
    if isempty(pl):
        return False, empty()

    if api.n_equal(v, head(pl)):
        return True, tail(pl)

    return contains_split(tail(pl), v)


def _contains_list(pl1, pl2):
    if isempty(pl2):
        return True
    if isempty(pl1):
        return False

    if not api.n_equal(head(pl1), head(pl2)):
        return False
    else:
        return _contains_list(tail(pl1), tail(pl2))


def contains_list(pl1, pl2):
    if isempty(pl2):
        return True
    if isempty(pl1):
        return False

    find, pl1_tail = contains_split(pl1, head(pl2))
    if not find:
        return False
    return _contains_list(pl1_tail, tail(pl2))


def equal_with(pl1, pl2, condition):
    if isempty(pl2) and isempty(pl1):
        return True
    if isempty(pl1):
        return False
    if isempty(pl2):
        return False

    if not condition(head(pl1), head(pl2)):
        return False
    else:
        return equal_with(tail(pl1), tail(pl2), condition)


def equal(pl1, pl2):
    return equal_with(pl1, pl2, api.n_equal)


######################################################

def _substract(pl1, pl2, result):
    if isempty(pl1):
        return result

    if not contains(pl2, head(pl1)):
        return _substract(tail(pl1), pl2, prepend(head(pl1), result))
    else:
        return _substract(tail(pl1), pl2, result)


def substract(pl1, pl2):
    assert space.islist(pl1)
    assert space.islist(pl2)
    return reverse(_substract(pl1, pl2, empty()))


######################################################

def index(pl, elem):
    assert space.islist(pl)
    cur = pl
    idx = 0
    while True:
        if isempty(cur):
            return -1
        if api.n_equal(head(cur), elem):
            return idx
        idx += 1
        cur = cur.tail


def fmap(func, pl):
    assert space.islist(pl)
    if isempty(pl):
        return empty()

    return prepend(func(head(pl)), fmap(func, tail(pl)))


def each(func, pl):
    assert space.islist(pl)
    if isempty(pl):
        return None

    result = func(head(pl))
    if result is not None:
        return result

    return each(func, tail(pl))


##############################################################

def _reverse_acc(pl, result):
    if isempty(pl):
        return result
    return _reverse_acc(tail(pl), prepend(head(pl), result))


def reverse(pl):
    assert space.islist(pl)
    return _reverse_acc(pl, empty())


##############################################################

def _hash(acc, el):
    from obin.types import api
    from rpython.rlib.rarithmetic import intmask
    y = api.n_hash(el)
    return intmask((1000003 * acc) ^ y)


def compute_hash(pl):
    assert space.islist(pl)
    return foldl(_hash, 0x345678, pl)


##############################################################

def plist_vec(process, vec):
    items = vec.to_l()
    return plist(items)


def plist_tuple(process, tupl):
    items = tupl.to_l()
    return plist(items)


def plist(items):
    lst = empty()
    for item in reversed(items):
        lst = prepend(item, lst)
    return lst


def plist1(item):
    return prepend(item, empty())
