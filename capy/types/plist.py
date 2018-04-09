from capy.types.root import W_Root
from capy.types import space
from capy.types import api
from capy.runtime import error


class W_PList(W_Root):
    def __init__(self, head, tail):
        self.head = head
        self.tail = tail

    def __iter__(self):
        cur = self
        while not is_empty(cur):
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
            if is_empty(cur):
                els.append("()")
                break
            els.append("%s" % (cur.head))
            cur = cur.tail
        return str(els)

    def _to_string_(self):
        from capy.types import api
        els = []
        cur = self
        while True:
            if is_empty(cur):
                break
            els.append(api.to_s(head(cur)))
            cur = cur.tail
        return "[%s]" % (", ".join(els))

    def _to_repr_(self):
        return self._to_string_()

    def _length_(self):
        return length(self)

    def _get_index_(self, obj):
        return index(self, obj)

    # def _at_index_(self, i):
    #     if i < 0:
    #         return space.newnil()
    #     return nth(self, i)

    def _has_(self, key):
        return contains(self, key)

    def _at_index_(self, i):
        if i < 0:
            return space.newvoid()
        return nth(self, i)

    def _at_(self, key):
        if not space.isint(key):
            error.throw_1(error.Errors.TYPE_ERROR, key)

        int_index = api.to_i(key)
        if int_index < 0:
            return space.newvoid()

        return nth(self, int_index)

    def _put_(self, k, v):
        from capy.types import api
        error.affirm_type(k, space.isint)
        i = api.to_i(k)
        return update(self, i, v)

    def _put_at_index_(self, i, v):
        return update(self, i, v)

    def _type_(self, process):
        return process.std.classes.List

    def _equal_(self, other):
        if not space.islist(other):
            return False

        if is_empty(other) and is_empty(self):
            return True
        return equal(self, other)

    def to_l(self):
        return [i for i in self]


__EMPTY__ = W_PList(space.newvoid(), space.newvoid())


def empty():
    return __EMPTY__


def to_tuple(pl):
    return space.newarray(pl.to_l())


def foldl(func, acc, pl):
    type_check(pl)
    if is_empty(pl):
        return acc

    return foldl(func,
                 func(head(pl), acc),
                 tail(pl))


def foldr(func, acc, pl):
    type_check(pl)
    if is_empty(pl):
        return acc

    return func(head(pl),
                foldr(func, acc, tail(pl)))


def is_empty(pl):
    return pl is __EMPTY__


def head(pl):
    type_check(pl)
    return pl.head


def type_check(pl):
    error.affirm_type(pl, space.islist)


def tail(pl):
    type_check(pl)
    return pl.tail


def split(pl):
    type_check(pl)
    return head(pl), tail(pl)


def _length_foldl(el, acc):
    return acc + 1


def length(pl):
    type_check(pl)
    return foldl(_length_foldl, 0, pl)


def cons(v, pl):
    error.affirm_any(v)
    type_check(pl)
    return W_PList(v, pl)


def cons_n_list(items, pl):
    type_check(pl)
    head = pl
    for item in reversed(items):
        head = cons(item, head)
    return head


def append(pl, v):
    type_check(pl)
    return insert(pl, length(pl), v)


def concat(pl1, pl2):
    type_check(pl1)
    type_check(pl2)
    return foldr(cons, pl2, pl1)


def pop(pl):
    type_check(pl)
    return pl.tail


def take(pl, count):
    type_check(pl)
    if count <= 0:
        return empty()

    if is_empty(pl):
        return error.throw_1(error.Errors.INDEX_ERROR, space.newint(count))
    return cons(head(pl), take(pop(pl), count - 1))


def drop(pl, count):
    type_check(pl)
    if count == 0:
        return pl
    if is_empty(pl):
        return error.throw_1(error.Errors.INDEX_ERROR, space.newint(count))

    return drop(tail(pl), count - 1)


##############################################

def _slice(pl, index, start, end):
    if is_empty(pl):
        return error.throw_3(error.Errors.SLICE_ERROR, space.newint(index),
                             space.newint(start), space.newint(end))

    if index < start:
        return _slice(tail(pl), index + 1, start, end)

    if index < end:
        return cons(head(pl), _slice(tail(pl), index + 1, start, end))

    return empty()


def slice(pl, start, end):
    type_check(pl)
    if start == end:
        return empty()

    error.affirm(start >= 0, u"Invalid slice : start < 0")
    error.affirm(end > start, u"Invalid slice : end <= start")
    error.affirm(end > 0, u"Invalid slice : end <= 0 start")

    # return take(drop(pl, start), end - 1)
    return _slice(pl, 0, start, end)


##############################################

def _nth(pl, index):
    from capy.types.space import newvoid
    if index == 0:
        return head(pl)
    if is_empty(pl):
        return newvoid()
    return _nth(tail(pl), index - 1)


def nth(pl, index):
    type_check(pl)
    error.affirm(index >= 0, u"List nth: index < 0")
    return _nth(pl, index)


##############################################

def _nth_tail(pl, index):
    from capy.types.space import newvoid
    if index == 0:
        return tail(pl)
    if is_empty(pl):
        return newvoid()
    return _nth_tail(tail(pl), index - 1)


def nth_tail(pl, index):
    type_check(pl)
    error.affirm(index >= 0, u"Invalid index index < 0")
    return _nth_tail(pl, index)


def insert(pl, index, v):
    type_check(pl)
    if index == 0:
        return cons(v, pl)

    if is_empty(pl):
        return error.throw_1(error.Errors.INDEX_ERROR, space.newint(index))

    return W_PList(head(pl), insert(tail(pl), index - 1, v))


def update(pl, index, v):
    type_check(pl)
    if index == 0:
        return cons(v, tail(pl))

    if is_empty(tail(pl)):
        return error.throw_1(error.Errors.INDEX_ERROR, space.newint(index))

    return W_PList(head(pl), update(tail(pl), index - 1, v))


def remove_all(pl, v):
    type_check(pl)
    if is_empty(pl):
        return pl

    if api.equal_b(v, head(pl)):
        l = remove_all(tail(pl), v)
        return l
    l = W_PList(head(pl), remove_all(tail(pl), v))
    return l


def remove(pl, v):
    type_check(pl)
    from capy.types import api
    if is_empty(pl):
        return error.throw_1(error.Errors.VALUE_ERROR, pl)

    if api.equal_b(v, head(pl)):
        return tail(pl)

    return W_PList(head(pl), remove(tail(pl), v))


def remove_silent(pl, v):
    type_check(pl)
    from capy.types import api
    if is_empty(pl):
        return empty()

    if api.equal_b(v, head(pl)):
        return tail(pl)

    return W_PList(head(pl), remove_silent(tail(pl), v))


########################################################################

def count(pl, v):
    count = 0
    for i in pl:
        if api.equal_b(i, v):
            count += 1
    return count


def is_hetero(pl):
    for i in pl:
        if count(pl, i) > 1:
            return False
    return True


def not_unique_item(pl):
    for i in pl:
        if count(pl, i) > 1:
            return i
    return None


def unique(pl, predicate=None):
    if not predicate:
        predicate = api.equal_b

    lst = empty()
    for item in pl:
        if not contains_with(lst, item, predicate):
            lst = cons(item, lst)

    return reverse(lst)


########################################################################


def contains_with(pl, v, condition):
    type_check(pl)
    if is_empty(pl):
        return False

    if condition(v, head(pl)):
        return True

    return contains_with(tail(pl), v, condition)


def contains(pl, v):
    return contains_with(pl, v, api.equal_b)


########################################################################

def find_with(pl, v, condition):
    type_check(pl)
    if is_empty(pl):
        return space.newvoid()

    if condition(v, head(pl)):
        return head(pl)

    return find_with(tail(pl), v, condition)


def find(pl, v):
    return contains_with(pl, v, api.equal_b)


############################################################

def contains_split(pl, v):
    type_check(pl)
    if is_empty(pl):
        return False, empty()

    if api.equal_b(v, head(pl)):
        return True, tail(pl)

    return contains_split(tail(pl), v)


def _contains_list(pl1, pl2):
    if is_empty(pl2):
        return True
    if is_empty(pl1):
        return False

    if not api.equal_b(head(pl1), head(pl2)):
        return False
    else:
        return _contains_list(tail(pl1), tail(pl2))


def contains_list(pl1, pl2):
    if is_empty(pl2):
        return True
    if is_empty(pl1):
        return False

    find, pl1_tail = contains_split(pl1, head(pl2))
    if not find:
        return False
    return _contains_list(pl1_tail, tail(pl2))


def equal_with(pl1, pl2, condition):
    if is_empty(pl2) and is_empty(pl1):
        return True
    if is_empty(pl1):
        return False
    if is_empty(pl2):
        return False

    if not condition(head(pl1), head(pl2)):
        return False
    else:
        return equal_with(tail(pl1), tail(pl2), condition)


def equal(pl1, pl2):
    return equal_with(pl1, pl2, api.equal_b)


######################################################

def _substract(pl1, pl2, result):
    if is_empty(pl1):
        return result

    if not contains(pl2, head(pl1)):
        return _substract(tail(pl1), pl2, cons(head(pl1), result))
    else:
        return _substract(tail(pl1), pl2, result)


def substract(pl1, pl2):
    type_check(pl1)
    type_check(pl2)
    return reverse(_substract(pl1, pl2, empty()))


######################################################

def index(pl, elem):
    type_check(pl)
    cur = pl
    idx = 0
    while True:
        if is_empty(cur):
            return -1
        if api.equal_b(head(cur), elem):
            return idx
        idx += 1
        cur = cur.tail


def fmap(func, pl):
    type_check(pl)
    if is_empty(pl):
        return empty()

    return cons(func(head(pl)), fmap(func, tail(pl)))


def each(func, pl):
    type_check(pl)
    if is_empty(pl):
        return None

    result = func(head(pl))
    if result is not None:
        return result

    return each(func, tail(pl))


##############################################################

def _reverse_acc(pl, result):
    if is_empty(pl):
        return result
    return _reverse_acc(tail(pl), cons(head(pl), result))


def reverse(pl):
    type_check(pl)
    return _reverse_acc(pl, empty())


##############################################################

def _hash(el, acc):
    from capy.types import api
    from capy.misc.platform import rarithmetic
    y = api.hash_i(el)
    return rarithmetic.intmask((1000003 * acc) ^ y)


def compute_hash(pl):
    type_check(pl)
    return foldl(_hash, 0x345678, pl)


##############################################################

def diff(pl1, pl2):
    items = []
    for el in pl1:
        if not contains(pl2, el):
            items.append(el)

    return plist(items)


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
        lst = cons(item, lst)
    return lst


def plist1(item):
    return cons(item, empty())


def plist_unique(items, predicate=None):
    if not predicate:
        predicate = api.equal_b
    lst = empty()
    for item in reversed(items):
        if not contains_with(lst, item, predicate):
            lst = cons(item, lst)
    return lst
