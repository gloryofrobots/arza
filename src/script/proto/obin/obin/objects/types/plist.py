from obin.objects.types.root import W_Root
from obin.objects import space
from obin.objects import api


class W_PList(W_Root):
    def __init__(self, head, tail):
        self.head = head
        self.tail = tail

    def __iter__(self):
        cur = self
        while not isempty(cur):
            yield head(cur)
            cur = cur.tail

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
        from obin.objects import api
        els = []
        cur = self
        while True:
            if isempty(cur):
                break
            els.append(api.to_native_string(head(cur)))
            cur = cur.tail
        return "[%s]" % (", ".join(els))

    def _length_(self):
        return length(self)

    def _get_index_(self, obj):
        return index(self, obj)

    def _at_(self, key):
        from obin.objects.space import newundefined
        from obin.objects import api
        int_index = api.to_native_integer(key)
        if int_index < 0:
            return newundefined()

        return nth(self, int_index)

    def _slice_(self, start, end):
        from obin.objects.space import isundefined, newundefined
        from obin.objects import api

        if isundefined(start):
            start_index = 0
        else:
            start_index = api.to_native_integer(start)

        # INTELLIGENT ERROR HERE, BECAUSE LISTS DON`T SUPPORT RELATIVE SLICING
        if start_index < 0:
            return newundefined()

        if isundefined(end):
            return drop(self, start_index)
        else:
            end_index = api.to_native_integer(end)

        # INTELLIGENT ERROR HERE, BECAUSE LISTS DON`T SUPPORT RELATIVE SLICING
        if end_index < 0:
            return newundefined()
        return slice(self, start_index, end_index)

    def _equal_(self, other):
        if isempty(other) and isempty(self):
            return True
        return False

__EMPTY__ = W_PList(space.newundefined(), space.newundefined())


def empty():
    return __EMPTY__


def foldl(func, acc, pl):
    if isempty(pl):
        return acc

    return foldl(func,
                 func(acc, head(pl)),
                 tail(pl))


def foldr(func, acc, pl):
    if isempty(pl):
        return acc

    return func(head(pl),
                foldr(func, acc, tail(pl)))


def isempty(pl):
    return pl is __EMPTY__


def head(pl):
    return pl.head


def tail(pl):
    return pl.tail


def split(pl):
    return head(pl), tail(pl)


def _length_foldl(acc, el):
    return acc + 1


def length(pl):
    return foldl(_length_foldl, 0, pl)


def prepend(v, pl):
    assert v is not None
    return W_PList(v, pl)


def cons_n_list(items, pl):
    head = pl
    for item in reversed(items):
        head = prepend(item, head)
    return head


def append(pl, v):
    insert(pl, pl.count, v)


def concat(pl1, pl2):
    return foldr(prepend, pl2, pl1)


def pop(pl):
    return pl.tail


def take(pl, count):
    if count <= 0:
        return empty()

    if isempty(pl):
        raise RuntimeError("List to small for operation")
    return prepend(head(pl), take(pop(pl), count - 1))


def drop(pl, count):
    if count == 0:
        return pl
    if isempty(pl):
        raise RuntimeError("List to small for operation")

    return drop(tail(pl), count - 1)


##############################################

def _slice(pl, index, start, end):
    if isempty(pl):
        raise RuntimeError("List to small for operation")

    if index < start:
        return _slice(tail(pl), index + 1, start, end)

    if index < end:
        return prepend(head(pl), _slice(tail(pl), index + 1, start, end))

    return empty()


def slice(pl, start, end):
    assert start >= 0
    assert end > start
    assert end > 0
    # return take(drop(pl, start), end - 1)
    return _slice(pl, 0, start, end)


##############################################

def _nth(pl, index):
    from obin.objects.space import newundefined
    if index == 0:
        return head(pl)
    if isempty(pl):
        return newundefined()
    return nth(tail(pl), index - 1)


def nth(pl, index):
    assert index >= 0
    return _nth(pl, index)


def insert(pl, index, v):
    if index == 0:
        return prepend(v, pl)

    if isempty(pl):
        raise RuntimeError("Invalide Index")

    return W_PList(head(pl), insert(tail(pl), index - 1, v))


def remove_all(pl, v):
    if isempty(pl):
        return pl

    if api.n_equal(v, head(pl)):
        l = remove_all(tail(pl), v)
        return l
    l = W_PList(head(pl), remove_all(tail(pl), v))
    return l


def remove(pl, v):
    from obin.objects import api
    if isempty(pl):
        raise RuntimeError("Invalid value")

    if api.n_equal(v, head(pl)):
        return tail(pl)

    return W_PList(head(pl), remove(tail(pl), v))


def contains(pl, v):
    from obin.objects import api
    if isempty(pl):
        return False

    if api.n_equal(v, head(pl)):
        return True

    return contains(tail(pl), v)


######################################################

def _substract(pl1, pl2, result):
    if isempty(pl1):
        return result

    if not contains(pl2, head(pl1)):
        return _substract(tail(pl1), pl2, prepend(head(pl1), result))
    else:
        return _substract(tail(pl1), pl2, result)


def substract(pl1, pl2):
    return reverse(_substract(pl1, pl2, empty()))


######################################################

def index(pl, elem):
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
    if isempty(pl):
        return empty()

    return prepend(func(head(pl)), fmap(func, tail(pl)))


def each(func, pl):
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
    return _reverse_acc(pl, empty())


##############################################################

def _hash(acc, el):
    from obin.objects import api
    from rpython.rlib.rarithmetic import intmask
    y = api.n_hash(el)
    return intmask((1000003 * acc) ^ y)


def compute_hash(pl):
    return foldl(_hash, 0x345678, pl)


##############################################################

def plist_vec(process, vec):
    items = vec.to_py_list()
    return plist(items)


def plist_tuple(process, tupl):
    items = tupl.to_py_list()
    return plist(items)


def plist(items):
    lst = empty()
    for item in reversed(items):
        lst = prepend(item, lst)
    return lst


def plist1(item):
    return prepend(item, empty())


##############################################################

def test():
    from obin.objects.space import newint
    from obin.objects import api
    def test_list(pl, check):
        check = make_test_data(check)
        assert length(pl) == len(check)
        for li, ci in zip(pl, check):
            if not api.n_equal(li.head, ci[0]):
                print "TEST FAILED", pl, check
                raise RuntimeError("Test Failed")

        print "TEST SUCCESS", pl

    def make_test_data(vals):
        w_vals = [newint(val) for val in vals]
        return zip(w_vals, reversed(range(1, len(w_vals) + 1)))

    ni = newint
    nis = lambda items: [newint(i) for i in items]

    l = plist(nis([0]))
    l1 = prepend(ni(1), l)
    l2 = prepend(ni(2), l1)
    l3 = prepend(ni(3), l2, )
    test_list(l3, [3, 2, 1, 0])
    l4 = insert(l3, 1, ni(44))
    test_list(l4, [3, 44, 2, 1, 0])

    l5 = insert(l4, 2, ni(55))
    test_list(l5, [3, 44, 55, 2, 1, 0])
    l6 = take(l5, 3)
    test_list(l6, [3, 44, 55])

    l7 = remove(l6, ni(44))
    test_list(l7, [3, 55])
    l7_1 = remove(l6, ni(55))
    test_list(l7_1, [3, 44])

    l8 = cons_n_list(nis([123, 124, 125, 123, 124, 125]), l7)
    test_list(l8, [123, 124, 125, 123, 124, 125, 3, 55])
    # print remove_all(l8, ni(125))
    l9 = reverse(l8)
    print l9
    l10 = concat(l8, l9)
    print l10

    def inc(el):
        from obin.objects import api, space
        return space.newint(api.to_native_integer(el) + 1)

    l11 = fmap(inc, l10)
    print l11
    l12 = plist(nis([1, 2, 3]))
    l13 = plist(nis([1, 2, 3, 4, 5]))
    l14 = substract(l13, l12)
    test_list(l14, [4, 5])
    # l9 = newlist(nis([1,2,2,3,4,5,2,6,2,7]))
    # l9 = newlist(nis([1,2,3]))
    # print l9
    # l10 = remove_all(l9, ni(2))
    # print l10


if __name__ == "__main__":
    test()

"""

template<class T>
class List
{
    // Empty list
    List() {}
   // Cons
    List(T v, List const & tail)
        : _head(std::make_shared<Item>(v, tail._head)) {}
    // Singleton
    explicit List(T v) : _head(std::make_shared<Item>(v)) {}
    // From initializer list


    bool isEmpty() const { return !_head; } // conversion to bool
    T front() const
    {
        assert(!isEmpty());
        return _head->_val;
    }
    List popped_front() const
    {
        assert(!isEmpty());
        return List(_head->_next);
    }
    // Additional utilities
    List pushed_front(T v) const
    {
        return List(v, *this);
    }
    List take(int n)
    {
        if (n <= 0 || isEmpty()) return List();
        return popped_front().take(n - 1).pushed_front(front());
    }
    List insertedAt(int i, T v) const
    {
        if (i == 0)
            return pushed_front(v);
        else {
            assert(!isEmpty());
            return List<T>(front(), popped_front().insertedAt(i - 1, v));
        }
    }
    List removed(T v) const
    {
        if (isEmpty()) return List();
        if (v == front())
            return popped_front().removed(v);
        return List(front(), popped_front().removed(v));
    }
    List removed1(T v) const
    {
        if (isEmpty()) return List();
        if (v == front())
            return popped_front();
        return List(front(), popped_front().removed(v));
    }
    bool member(T v) const
    {
        if (isEmpty()) return false;
        if (v == front()) return true;
        return popped_front().member(v);
    }
    template<class F>
    void forEach(F f) const
    {
        Item const * it = _head.get();
        while (it != nullptr)
        {
            f(it->_val);
            it = it->_next.get();
        }
    }

    friend class FwdListIter<T>;
    // For debugging
    int headCount() const { return _head.use_count(); }
private:
    std::shared_ptr<const Item> _head;
};

template<class T, class P>
bool all(List<T> const & lst, P & p)
{
    if (lst.isEmpty())
        return true;
    if (!p(lst.front()))
        return false;
    return all(lst.popped_front(), p);
}

template<class T>
class FwdListIter : public std::iterator<std::forward_iterator_tag, T>
{
public:
    FwdListIter() {} // end
    FwdListIter(List<T> const & lst) : _cur(lst._head)
    {}
    T operator*() const { return _cur->_val; }
    FwdListIter & operator++()
    {
        _cur = _cur->_next;
        return *this;
    }
    bool operator==(FwdListIter<T> const & other)
    {
        return _cur == other._cur;
    }
    bool operator!=(FwdListIter<T> const & other)
    {
        return !(*this == other);
    }
private:
    std::shared_ptr<const typename List<T>::Item> _cur;
};

template<class T>
class OutListIter : public std::iterator<std::output_iterator_tag, T>
{
public:
    OutListIter() {}
    T & operator*() { return _val; }
    OutListIter & operator++()
    {
        _lst = List<T>(_val, _lst);
        return *this;
    }
    List<T> getList() const { return _lst; }
private:
    T _val;
    List<T> _lst;
};


namespace std
{
    template<class T>
    FwdListIter<T> begin(List<T> const & lst)
    {
        return FwdListIter<T>(lst);
    }
    template<class T>
    FwdListIter<T> end(List<T> const & lst)
    {
        return FwdListIter<T>();
    }
}

template<class T>
List<T> concat(List<T> const & a, List<T> const & b)
{
    if (a.isEmpty())
        return b;
    return List<T>(a.front(), concat(a.popped_front(), b));
}

template<class T, class F>
auto fmap(F f, List<T> lst) -> List<decltype(f(lst.front()))>
{
    using U = decltype(f(lst.front()));
    static_assert(std::is_convertible<F, std::function<U(T)>>::value,
        "fmap requires a function type U(T)");
    if (lst.isEmpty())
        return List<U>();
    else
        return List<U>(f(lst.front()), fmap(f, lst.popped_front()));
}

template<class T, class P>
List<T> filter(P p, List<T> lst)
{
    static_assert(std::is_convertible<P, std::function<bool(T)>>::value,
                 "filter requires a function type bool(T)");
    if (lst.isEmpty())
        return List<T>();
    if (p(lst.front()))
        return List<T>(lst.front(), filter(p, lst.popped_front()));
    else
        return filter(p, lst.popped_front());
}

template<class T, class U, class F>
U foldr(F f, U acc, List<T> lst)
{
    static_assert(std::is_convertible<F, std::function<U(T, U)>>::value,
                 "foldr requires a function type U(T, U)");
    if (lst.isEmpty())
        return acc;
    else
        return f(lst.front(), foldr(f, acc, lst.popped_front()));
}

template<class T, class U, class F>
U foldl(F f, U acc, List<T> lst)
{
    static_assert(std::is_convertible<F, std::function<U(U, T)>>::value,
                 "foldl requires a function type U(U, T)");
    if (lst.isEmpty())
        return acc;
    else
        return foldl(f, f(acc, lst.front()), lst.popped_front());
}

// Set difference a \ b
template<class T>
List<T> set_diff(List<T> const & as, List<T> const & bs)
{
    return foldl([](List<T> const & acc, T x) {
        return acc.removed(x);
    }, as, bs);
}

// Set union of two lists, xs u ys
// Assume no duplicates inside either list
template<class T>
List<T> set_union(List<T> const & xs, List<T> const & ys)
{
    // xs u ys = (ys \ xs) ++ xs
    // removed all xs from ys
    auto trimmed = foldl([](List<T> const & acc, T x) {
        return acc.removed(x);
    }, ys, xs);
    return concat(trimmed, xs);
}

template<class T>
List<T> concatAll(List<List<T>> const & xss)
{
    if (xss.isEmpty()) return List<T>();
    return concat(xss.front(), concatAll(xss.popped_front()));
}

// consumes the list when called:
// forEach(std::move(lst), f);

template<class T, class F>
void forEach(List<T> lst, F f)
{
    static_assert(std::is_convertible<F, std::function<void(T)>>::value,
                 "forEach requires a function type void(T)");
    while (!lst.isEmpty()) {
        f(lst.front());
        lst = lst.popped_front();
    }
}

template<class Beg, class End>
auto fromIt(Beg it, End end) -> List<typename Beg::value_type>
{
    typedef typename Beg::value_type T;
    if (it == end)
        return List<T>();
    T item = *it;
    return List<T>(item, fromIt(++it, end));
}

template<class T, class F>
List<T> iterateN(F f, T init, int count)
{
    if (count <= 0) return List<T>();
    return iterateN(f, f(init), count - 1).pushed_front(init);
}

// Pass lst by value not reference!
template<class T>
void printRaw(List<T> lst)
{
    if (lst.isEmpty()) {
        std::cout << std::endl;
    }
    else {
        std::cout << "(" << lst.front() << ", " << lst.headCount() - 1 << ") ";
        printRaw(lst.popped_front());
    }
}

template<class T>
std::ostream& operator<<(std::ostream& os, List<T> const & lst)
{
    os << "[";
    forEach(lst, [&os](T v) {
        os << v << " ";
    });
    os << "]";
    return os;
}

template<class T>
List<T> reversed(List<T> const & lst)
{
    return foldl([](List<T> const & acc, T v)
    {
        return List<T>(v, acc);
    }, List<T>(), lst);
}

#endif

"""
