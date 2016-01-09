from obin.objects.types.root import W_Root
from obin.objects import space
from obin.objects import api


class W_List(W_Root):
    def __init__(self, head, tail):
        self.head = head
        self.tail = tail

    def __iter__(self):
        cur = self
        while not isempty(cur):
            yield cur
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
        return "[%s]" % (":".join(els))

    def _length_(self):
        return length(self)

    def _get_index_(self, obj):
        return index(self, obj)


def empty():
    from obin.objects.space import newundefined
    return W_List(newundefined(), newundefined())


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
    from obin.objects.space import isundefined
    return isundefined(head(pl))


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
    return W_List(v, pl)


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


def insert(pl, index, v):
    if index == 0:
        return prepend(v, pl)

    if isempty(pl):
        raise RuntimeError("Invalide Index")

    return W_List(head(pl), insert(tail(pl), index - 1, v))


def remove_all(pl, v):
    if isempty(pl):
        return pl

    if api.n_equal(v, head(pl)):
        l = remove_all(tail(pl), v)
        return l
    l = W_List(head(pl), remove_all(tail(pl), v))
    return l


def remove(pl, v):
    from obin.objects import api
    if isempty(pl):
        raise RuntimeError("Invalid value")

    if api.n_equal(v, head(pl)):
        return tail(pl)

    return W_List(head(pl), remove(tail(pl), v))


def contains(pl, v):
    from obin.objects import api
    if isempty(pl):
        return False

    if api.n_equal(v, head(pl)):
        return True

    return contains(tail(pl), v)


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
    items = vec.to_n_list()
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



/*
 * Copyright 1997-2006 Sun Microsystems, Inc.  All Rights Reserved.
 * DO NOT ALTER OR REMOVE COPYRIGHT NOTICES OR THIS FILE HEADER.
 *
 * This code is free software; you can redistribute it and/or modify it
 * under the terms of the GNU General Public License version 2 only, as
 * published by the Free Software Foundation.  Sun designates this
 * particular file as subject to the "Classpath" exception as provided
 * by Sun in the LICENSE file that accompanied this code.
 *
 * This code is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
 * version 2 for more details (a copy is included in the LICENSE file that
 * accompanied this code).
 *
 * You should have received a copy of the GNU General Public License version
 * 2 along with this work; if not, write to the Free Software Foundation,
 * Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA.
 *
 * Please contact Sun Microsystems, Inc., 4150 Network Circle, Santa Clara,
 * CA 95054 USA or visit www.sun.com if you need additional information or
 * have any questions.
 */

package java.util;

/**
 * This class provides a skeletal implementation of the <tt>List</tt>
 * interface to minimize the effort required to implement this interface
 * backed by a "sequential access" data store (such as a linked list).  For
 * random access data (such as an array), <tt>AbstractList</tt> should be used
 * in preference to this class.<p>
 *
 * This class is the opposite of the <tt>AbstractList</tt> class in the sense
 * that it implements the "random access" methods (<tt>get(int index)</tt>,
 * <tt>set(int index, E element)</tt>, <tt>add(int index, E element)</tt> and
 * <tt>remove(int index)</tt>) on top of the list's list iterator, instead of
 * the other way around.<p>
 *
 * To implement a list the programmer needs only to extend this class and
 * provide implementations for the <tt>listIterator</tt> and <tt>size</tt>
 * methods.  For an unmodifiable list, the programmer need only implement the
 * list iterator's <tt>hasNext</tt>, <tt>next</tt>, <tt>hasPrevious</tt>,
 * <tt>previous</tt> and <tt>index</tt> methods.<p>
 *
 * For a modifiable list the programmer should additionally implement the list
 * iterator's <tt>set</tt> method.  For a variable-size list the programmer
 * should additionally implement the list iterator's <tt>remove</tt> and
 * <tt>add</tt> methods.<p>
 *
 * The programmer should generally provide a void (no argument) and collection
 * constructor, as per the recommendation in the <tt>Collection</tt> interface
 * specification.<p>
 *
 * This class is a member of the
 * <a href="{@docRoot}/../technotes/guides/collections/index.html">
 * Java Collections Framework</a>.
 *
 * @author  Josh Bloch
 * @author  Neal Gafter
 * @see Collection
 * @see List
 * @see AbstractList
 * @see AbstractCollection
 * @since 1.2
 */

public abstract class AbstractSequentialList<E> extends AbstractList<E> {
    /**
     * Sole constructor.  (For invocation by subclass constructors, typically
     * implicit.)
     */
    protected AbstractSequentialList() {
    }

    /**
     * Returns the element at the specified position in this list.
     *
     * <p>This implementation first gets a list iterator pointing to the
     * indexed element (with <tt>listIterator(index)</tt>).  Then, it gets
     * the element using <tt>ListIterator.next</tt> and returns it.
     *
     * @throws IndexOutOfBoundsException {@inheritDoc}
     */
    public E get(int index) {
        try {
            return listIterator(index).next();
        } catch (NoSuchElementException exc) {
            throw new IndexOutOfBoundsException("Index: "+index);
        }
    }

    /**
     * Replaces the element at the specified position in this list with the
     * specified element (optional operation).
     *
     * <p>This implementation first gets a list iterator pointing to the
     * indexed element (with <tt>listIterator(index)</tt>).  Then, it gets
     * the current element using <tt>ListIterator.next</tt> and replaces it
     * with <tt>ListIterator.set</tt>.
     *
     * <p>Note that this implementation will throw an
     * <tt>UnsupportedOperationException</tt> if the list iterator does not
     * implement the <tt>set</tt> operation.
     *
     * @throws UnsupportedOperationException {@inheritDoc}
     * @throws ClassCastException            {@inheritDoc}
     * @throws NullPointerException          {@inheritDoc}
     * @throws IllegalArgumentException      {@inheritDoc}
     * @throws IndexOutOfBoundsException     {@inheritDoc}
     */
    public E set(int index, E element) {
        try {
            ListIterator<E> e = listIterator(index);
            E oldVal = e.next();
            e.set(element);
            return oldVal;
        } catch (NoSuchElementException exc) {
            throw new IndexOutOfBoundsException("Index: "+index);
        }
    }

    /**
     * Inserts the specified element at the specified position in this list
     * (optional operation).  Shifts the element currently at that position
     * (if any) and any subsequent elements to the right (adds one to their
     * indices).
     *
     * <p>This implementation first gets a list iterator pointing to the
     * indexed element (with <tt>listIterator(index)</tt>).  Then, it
     * inserts the specified element with <tt>ListIterator.add</tt>.
     *
     * <p>Note that this implementation will throw an
     * <tt>UnsupportedOperationException</tt> if the list iterator does not
     * implement the <tt>add</tt> operation.
     *
     * @throws UnsupportedOperationException {@inheritDoc}
     * @throws ClassCastException            {@inheritDoc}
     * @throws NullPointerException          {@inheritDoc}
     * @throws IllegalArgumentException      {@inheritDoc}
     * @throws IndexOutOfBoundsException     {@inheritDoc}
     */
    public void add(int index, E element) {
        try {
            listIterator(index).add(element);
        } catch (NoSuchElementException exc) {
            throw new IndexOutOfBoundsException("Index: "+index);
        }
    }

    /**
     * Removes the element at the specified position in this list (optional
     * operation).  Shifts any subsequent elements to the left (subtracts one
     * from their indices).  Returns the element that was removed from the
     * list.
     *
     * <p>This implementation first gets a list iterator pointing to the
     * indexed element (with <tt>listIterator(index)</tt>).  Then, it removes
     * the element with <tt>ListIterator.remove</tt>.
     *
     * <p>Note that this implementation will throw an
     * <tt>UnsupportedOperationException</tt> if the list iterator does not
     * implement the <tt>remove</tt> operation.
     *
     * @throws UnsupportedOperationException {@inheritDoc}
     * @throws IndexOutOfBoundsException     {@inheritDoc}
     */
    public E remove(int index) {
        try {
            ListIterator<E> e = listIterator(index);
            E outCast = e.next();
            e.remove();
            return outCast;
        } catch (NoSuchElementException exc) {
            throw new IndexOutOfBoundsException("Index: "+index);
        }
    }


    // Bulk Operations

    /**
     * Inserts all of the elements in the specified collection into this
     * list at the specified position (optional operation).  Shifts the
     * element currently at that position (if any) and any subsequent
     * elements to the right (increases their indices).  The new elements
     * will appear in this list in the order that they are returned by the
     * specified collection's iterator.  The behavior of this operation is
     * undefined if the specified collection is modified while the
     * operation is in progress.  (Note that this will occur if the specified
     * collection is this list, and it's nonempty.)
     *
     * <p>This implementation gets an iterator over the specified collection and
     * a list iterator over this list pointing to the indexed element (with
     * <tt>listIterator(index)</tt>).  Then, it iterates over the specified
     * collection, inserting the elements obtained from the iterator into this
     * list, one at a time, using <tt>ListIterator.add</tt> followed by
     * <tt>ListIterator.next</tt> (to skip over the added element).
     *
     * <p>Note that this implementation will throw an
     * <tt>UnsupportedOperationException</tt> if the list iterator returned by
     * the <tt>listIterator</tt> method does not implement the <tt>add</tt>
     * operation.
     *
     * @throws UnsupportedOperationException {@inheritDoc}
     * @throws ClassCastException            {@inheritDoc}
     * @throws NullPointerException          {@inheritDoc}
     * @throws IllegalArgumentException      {@inheritDoc}
     * @throws IndexOutOfBoundsException     {@inheritDoc}
     */
    public boolean addAll(int index, Collection<? extends E> c) {
        try {
            boolean modified = false;
            ListIterator<E> e1 = listIterator(index);
            Iterator<? extends E> e2 = c.iterator();
            while (e2.hasNext()) {
                e1.add(e2.next());
                modified = true;
            }
            return modified;
        } catch (NoSuchElementException exc) {
            throw new IndexOutOfBoundsException("Index: "+index);
        }
    }


    // Iterators

    /**
     * Returns an iterator over the elements in this list (in proper
     * sequence).<p>
     *
     * This implementation merely returns a list iterator over the list.
     *
     * @return an iterator over the elements in this list (in proper sequence)
     */
    public Iterator<E> iterator() {
        return listIterator();
    }

    /**
     * Returns a list iterator over the elements in this list (in proper
     * sequence).
     *
     * @param  index index of first element to be returned from the list
     *         iterator (by a call to the <code>next</code> method)
     * @return a list iterator over the elements in this list (in proper
     *         sequence)
     * @throws IndexOutOfBoundsException {@inheritDoc}
     */
    public abstract ListIterator<E> listIterator(int index);
}



/*
 * Copyright 1997-2007 Sun Microsystems, Inc.  All Rights Reserved.
 * DO NOT ALTER OR REMOVE COPYRIGHT NOTICES OR THIS FILE HEADER.
 *
 * This code is free software; you can redistribute it and/or modify it
 * under the terms of the GNU General Public License version 2 only, as
 * published by the Free Software Foundation.  Sun designates this
 * particular file as subject to the "Classpath" exception as provided
 * by Sun in the LICENSE file that accompanied this code.
 *
 * This code is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
 * version 2 for more details (a copy is included in the LICENSE file that
 * accompanied this code).
 *
 * You should have received a copy of the GNU General Public License version
 * 2 along with this work; if not, write to the Free Software Foundation,
 * Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA.
 *
 * Please contact Sun Microsystems, Inc., 4150 Network Circle, Santa Clara,
 * CA 95054 USA or visit www.sun.com if you need additional information or
 * have any questions.
 */

package java.util;

/**
 * This class provides a skeletal implementation of the {@link List}
 * interface to minimize the effort required to implement this interface
 * backed by a "random access" data store (such as an array).  For sequential
 * access data (such as a linked list), {@link AbstractSequentialList} should
 * be used in preference to this class.
 *
 * <p>To implement an unmodifiable list, the programmer needs only to extend
 * this class and provide implementations for the {@link #get(int)} and
 * {@link List#size() size()} methods.
 *
 * <p>To implement a modifiable list, the programmer must additionally
 * override the {@link #set(int, Object) set(int, E)} method (which otherwise
 * throws an {@code UnsupportedOperationException}).  If the list is
 * variable-size the programmer must additionally override the
 * {@link #add(int, Object) add(int, E)} and {@link #remove(int)} methods.
 *
 * <p>The programmer should generally provide a void (no argument) and collection
 * constructor, as per the recommendation in the {@link Collection} interface
 * specification.
 *
 * <p>Unlike the other abstract collection implementations, the programmer does
 * <i>not</i> have to provide an iterator implementation; the iterator and
 * list iterator are implemented by this class, on top of the "random access"
 * methods:
 * {@link #get(int)},
 * {@link #set(int, Object) set(int, E)},
 * {@link #add(int, Object) add(int, E)} and
 * {@link #remove(int)}.
 *
 * <p>The documentation for each non-abstract method in this class describes its
 * implementation in detail.  Each of these methods may be overridden if the
 * collection being implemented admits a more efficient implementation.
 *
 * <p>This class is a member of the
 * <a href="{@docRoot}/../technotes/guides/collections/index.html">
 * Java Collections Framework</a>.
 *
 * @author  Josh Bloch
 * @author  Neal Gafter
 * @since 1.2
 */

public abstract class AbstractList<E> extends AbstractCollection<E> implements List<E> {
    /**
     * Sole constructor.  (For invocation by subclass constructors, typically
     * implicit.)
     */
    protected AbstractList() {
    }

    /**
     * Appends the specified element to the end of this list (optional
     * operation).
     *
     * <p>Lists that support this operation may place limitations on what
     * elements may be added to this list.  In particular, some
     * lists will refuse to add null elements, and others will impose
     * restrictions on the type of elements that may be added.  List
     * classes should clearly specify in their documentation any restrictions
     * on what elements may be added.
     *
     * <p>This implementation calls {@code add(size(), e)}.
     *
     * <p>Note that this implementation throws an
     * {@code UnsupportedOperationException} unless
     * {@link #add(int, Object) add(int, E)} is overridden.
     *
     * @param e element to be appended to this list
     * @return {@code true} (as specified by {@link Collection#add})
     * @throws UnsupportedOperationException if the {@code add} operation
     *         is not supported by this list
     * @throws ClassCastException if the class of the specified element
     *         prevents it from being added to this list
     * @throws NullPointerException if the specified element is null and this
     *         list does not permit null elements
     * @throws IllegalArgumentException if some property of this element
     *         prevents it from being added to this list
     */
    public boolean add(E e) {
        add(size(), e);
        return true;
    }

    /**
     * {@inheritDoc}
     *
     * @throws IndexOutOfBoundsException {@inheritDoc}
     */
    abstract public E get(int index);

    /**
     * {@inheritDoc}
     *
     * <p>This implementation always throws an
     * {@code UnsupportedOperationException}.
     *
     * @throws UnsupportedOperationException {@inheritDoc}
     * @throws ClassCastException            {@inheritDoc}
     * @throws NullPointerException          {@inheritDoc}
     * @throws IllegalArgumentException      {@inheritDoc}
     * @throws IndexOutOfBoundsException     {@inheritDoc}
     */
    public E set(int index, E element) {
        throw new UnsupportedOperationException();
    }

    /**
     * {@inheritDoc}
     *
     * <p>This implementation always throws an
     * {@code UnsupportedOperationException}.
     *
     * @throws UnsupportedOperationException {@inheritDoc}
     * @throws ClassCastException            {@inheritDoc}
     * @throws NullPointerException          {@inheritDoc}
     * @throws IllegalArgumentException      {@inheritDoc}
     * @throws IndexOutOfBoundsException     {@inheritDoc}
     */
    public void add(int index, E element) {
        throw new UnsupportedOperationException();
    }

    /**
     * {@inheritDoc}
     *
     * <p>This implementation always throws an
     * {@code UnsupportedOperationException}.
     *
     * @throws UnsupportedOperationException {@inheritDoc}
     * @throws IndexOutOfBoundsException     {@inheritDoc}
     */
    public E remove(int index) {
        throw new UnsupportedOperationException();
    }


    // Search Operations

    /**
     * {@inheritDoc}
     *
     * <p>This implementation first gets a list iterator (with
     * {@code listIterator()}).  Then, it iterates over the list until the
     * specified element is found or the end of the list is reached.
     *
     * @throws ClassCastException   {@inheritDoc}
     * @throws NullPointerException {@inheritDoc}
     */
    public int indexOf(Object o) {
        ListIterator<E> e = listIterator();
        if (o==null) {
            while (e.hasNext())
                if (e.next()==null)
                    return e.previousIndex();
        } else {
            while (e.hasNext())
                if (o.equals(e.next()))
                    return e.previousIndex();
        }
        return -1;
    }

    /**
     * {@inheritDoc}
     *
     * <p>This implementation first gets a list iterator that points to the end
     * of the list (with {@code listIterator(size())}).  Then, it iterates
     * backwards over the list until the specified element is found, or the
     * beginning of the list is reached.
     *
     * @throws ClassCastException   {@inheritDoc}
     * @throws NullPointerException {@inheritDoc}
     */
    public int lastIndexOf(Object o) {
        ListIterator<E> e = listIterator(size());
        if (o==null) {
            while (e.hasPrevious())
                if (e.previous()==null)
                    return e.nextIndex();
        } else {
            while (e.hasPrevious())
                if (o.equals(e.previous()))
                    return e.nextIndex();
        }
        return -1;
    }


    // Bulk Operations

    /**
     * Removes all of the elements from this list (optional operation).
     * The list will be empty after this call returns.
     *
     * <p>This implementation calls {@code removeRange(0, size())}.
     *
     * <p>Note that this implementation throws an
     * {@code UnsupportedOperationException} unless {@code remove(int
     * index)} or {@code removeRange(int fromIndex, int toIndex)} is
     * overridden.
     *
     * @throws UnsupportedOperationException if the {@code clear} operation
     *         is not supported by this list
     */
    public void clear() {
        removeRange(0, size());
    }

    /**
     * {@inheritDoc}
     *
     * <p>This implementation gets an iterator over the specified collection
     * and iterates over it, inserting the elements obtained from the
     * iterator into this list at the appropriate position, one at a time,
     * using {@code add(int, E)}.
     * Many implementations will override this method for efficiency.
     *
     * <p>Note that this implementation throws an
     * {@code UnsupportedOperationException} unless
     * {@link #add(int, Object) add(int, E)} is overridden.
     *
     * @throws UnsupportedOperationException {@inheritDoc}
     * @throws ClassCastException            {@inheritDoc}
     * @throws NullPointerException          {@inheritDoc}
     * @throws IllegalArgumentException      {@inheritDoc}
     * @throws IndexOutOfBoundsException     {@inheritDoc}
     */
    public boolean addAll(int index, Collection<? extends E> c) {
        rangeCheckForAdd(index);
        boolean modified = false;
        Iterator<? extends E> e = c.iterator();
        while (e.hasNext()) {
            add(index++, e.next());
            modified = true;
        }
        return modified;
    }


    // Iterators

    /**
     * Returns an iterator over the elements in this list in proper sequence.
     *
     * <p>This implementation returns a straightforward implementation of the
     * iterator interface, relying on the backing list's {@code size()},
     * {@code get(int)}, and {@code remove(int)} methods.
     *
     * <p>Note that the iterator returned by this method will throw an
     * {@link UnsupportedOperationException} in response to its
     * {@code remove} method unless the list's {@code remove(int)} method is
     * overridden.
     *
     * <p>This implementation can be made to throw runtime exceptions in the
     * face of concurrent modification, as described in the specification
     * for the (protected) {@link #modCount} field.
     *
     * @return an iterator over the elements in this list in proper sequence
     */
    public Iterator<E> iterator() {
        return new Itr();
    }

    /**
     * {@inheritDoc}
     *
     * <p>This implementation returns {@code listIterator(0)}.
     *
     * @see #listIterator(int)
     */
    public ListIterator<E> listIterator() {
        return listIterator(0);
    }

    /**
     * {@inheritDoc}
     *
     * <p>This implementation returns a straightforward implementation of the
     * {@code ListIterator} interface that extends the implementation of the
     * {@code Iterator} interface returned by the {@code iterator()} method.
     * The {@code ListIterator} implementation relies on the backing list's
     * {@code get(int)}, {@code set(int, E)}, {@code add(int, E)}
     * and {@code remove(int)} methods.
     *
     * <p>Note that the list iterator returned by this implementation will
     * throw an {@link UnsupportedOperationException} in response to its
     * {@code remove}, {@code set} and {@code add} methods unless the
     * list's {@code remove(int)}, {@code set(int, E)}, and
     * {@code add(int, E)} methods are overridden.
     *
     * <p>This implementation can be made to throw runtime exceptions in the
     * face of concurrent modification, as described in the specification for
     * the (protected) {@link #modCount} field.
     *
     * @throws IndexOutOfBoundsException {@inheritDoc}
     */
    public ListIterator<E> listIterator(final int index) {
        rangeCheckForAdd(index);

        return new ListItr(index);
    }

    private class Itr implements Iterator<E> {
        /**
         * Index of element to be returned by subsequent call to next.
         */
        int cursor = 0;

        /**
         * Index of element returned by most recent call to next or
         * previous.  Reset to -1 if this element is deleted by a call
         * to remove.
         */
        int lastRet = -1;

        /**
         * The modCount value that the iterator believes that the backing
         * List should have.  If this expectation is violated, the iterator
         * has detected concurrent modification.
         */
        int expectedModCount = modCount;

        public boolean hasNext() {
            return cursor != size();
        }

        public E next() {
            checkForComodification();
            try {
                int i = cursor;
                E next = get(i);
                lastRet = i;
                cursor = i + 1;
                return next;
            } catch (IndexOutOfBoundsException e) {
                checkForComodification();
                throw new NoSuchElementException();
            }
        }

        public void remove() {
            if (lastRet < 0)
                throw new IllegalStateException();
            checkForComodification();

            try {
                AbstractList.this.remove(lastRet);
                if (lastRet < cursor)
                    cursor--;
                lastRet = -1;
                expectedModCount = modCount;
            } catch (IndexOutOfBoundsException e) {
                throw new ConcurrentModificationException();
            }
        }

        final void checkForComodification() {
            if (modCount != expectedModCount)
                throw new ConcurrentModificationException();
        }
    }

    private class ListItr extends Itr implements ListIterator<E> {
        ListItr(int index) {
            cursor = index;
        }

        public boolean hasPrevious() {
            return cursor != 0;
        }

        public E previous() {
            checkForComodification();
            try {
                int i = cursor - 1;
                E previous = get(i);
                lastRet = cursor = i;
                return previous;
            } catch (IndexOutOfBoundsException e) {
                checkForComodification();
                throw new NoSuchElementException();
            }
        }

        public int nextIndex() {
            return cursor;
        }

        public int previousIndex() {
            return cursor-1;
        }

        public void set(E e) {
            if (lastRet < 0)
                throw new IllegalStateException();
            checkForComodification();

            try {
                AbstractList.this.set(lastRet, e);
                expectedModCount = modCount;
            } catch (IndexOutOfBoundsException ex) {
                throw new ConcurrentModificationException();
            }
        }

        public void add(E e) {
            checkForComodification();

            try {
                int i = cursor;
                AbstractList.this.add(i, e);
                lastRet = -1;
                cursor = i + 1;
                expectedModCount = modCount;
            } catch (IndexOutOfBoundsException ex) {
                throw new ConcurrentModificationException();
            }
        }
    }

    /**
     * {@inheritDoc}
     *
     * <p>This implementation returns a list that subclasses
     * {@code AbstractList}.  The subclass stores, in private fields, the
     * offset of the subList within the backing list, the size of the subList
     * (which can change over its lifetime), and the expected
     * {@code modCount} value of the backing list.  There are two variants
     * of the subclass, one of which implements {@code RandomAccess}.
     * If this list implements {@code RandomAccess} the returned list will
     * be an instance of the subclass that implements {@code RandomAccess}.
     *
     * <p>The subclass's {@code set(int, E)}, {@code get(int)},
     * {@code add(int, E)}, {@code remove(int)}, {@code addAll(int,
     * Collection)} and {@code removeRange(int, int)} methods all
     * delegate to the corresponding methods on the backing abstract list,
     * after bounds-checking the index and adjusting for the offset.  The
     * {@code addAll(Collection c)} method merely returns {@code addAll(size,
     * c)}.
     *
     * <p>The {@code listIterator(int)} method returns a "wrapper object"
     * over a list iterator on the backing list, which is created with the
     * corresponding method on the backing list.  The {@code iterator} method
     * merely returns {@code listIterator()}, and the {@code size} method
     * merely returns the subclass's {@code size} field.
     *
     * <p>All methods first check to see if the actual {@code modCount} of
     * the backing list is equal to its expected value, and throw a
     * {@code ConcurrentModificationException} if it is not.
     *
     * @throws IndexOutOfBoundsException if an endpoint index value is out of range
     *         {@code (fromIndex < 0 || toIndex > size)}
     * @throws IllegalArgumentException if the endpoint indices are out of order
     *         {@code (fromIndex > toIndex)}
     */
    public List<E> subList(int fromIndex, int toIndex) {
        return (this instanceof RandomAccess ?
                new RandomAccessSubList<E>(this, fromIndex, toIndex) :
                new SubList<E>(this, fromIndex, toIndex));
    }

    // Comparison and hashing

    /**
     * Compares the specified object with this list for equality.  Returns
     * {@code true} if and only if the specified object is also a list, both
     * lists have the same size, and all corresponding pairs of elements in
     * the two lists are <i>equal</i>.  (Two elements {@code e1} and
     * {@code e2} are <i>equal</i> if {@code (e1==null ? e2==null :
     * e1.equals(e2))}.)  In other words, two lists are defined to be
     * equal if they contain the same elements in the same order.<p>
     *
     * This implementation first checks if the specified object is this
     * list. If so, it returns {@code true}; if not, it checks if the
     * specified object is a list. If not, it returns {@code false}; if so,
     * it iterates over both lists, comparing corresponding pairs of elements.
     * If any comparison returns {@code false}, this method returns
     * {@code false}.  If either iterator runs out of elements before the
     * other it returns {@code false} (as the lists are of unequal length);
     * otherwise it returns {@code true} when the iterations complete.
     *
     * @param o the object to be compared for equality with this list
     * @return {@code true} if the specified object is equal to this list
     */
    public boolean equals(Object o) {
        if (o == this)
            return true;
        if (!(o instanceof List))
            return false;

        ListIterator<E> e1 = listIterator();
        ListIterator e2 = ((List) o).listIterator();
        while(e1.hasNext() && e2.hasNext()) {
            E o1 = e1.next();
            Object o2 = e2.next();
            if (!(o1==null ? o2==null : o1.equals(o2)))
                return false;
        }
        return !(e1.hasNext() || e2.hasNext());
    }

    /**
     * Returns the hash code value for this list.
     *
     * <p>This implementation uses exactly the code that is used to define the
     * list hash function in the documentation for the {@link List#hashCode}
     * method.
     *
     * @return the hash code value for this list
     */
    public int hashCode() {
        int hashCode = 1;
        for (E e : this)
            hashCode = 31*hashCode + (e==null ? 0 : e.hashCode());
        return hashCode;
    }

    /**
     * Removes from this list all of the elements whose index is between
     * {@code fromIndex}, inclusive, and {@code toIndex}, exclusive.
     * Shifts any succeeding elements to the left (reduces their index).
     * This call shortens the list by {@code (toIndex - fromIndex)} elements.
     * (If {@code toIndex==fromIndex}, this operation has no effect.)
     *
     * <p>This method is called by the {@code clear} operation on this list
     * and its subLists.  Overriding this method to take advantage of
     * the internals of the list implementation can <i>substantially</i>
     * improve the performance of the {@code clear} operation on this list
     * and its subLists.
     *
     * <p>This implementation gets a list iterator positioned before
     * {@code fromIndex}, and repeatedly calls {@code ListIterator.next}
     * followed by {@code ListIterator.remove} until the entire range has
     * been removed.  <b>Note: if {@code ListIterator.remove} requires linear
     * time, this implementation requires quadratic time.</b>
     *
     * @param fromIndex index of first element to be removed
     * @param toIndex index after last element to be removed
     */
    protected void removeRange(int fromIndex, int toIndex) {
        ListIterator<E> it = listIterator(fromIndex);
        for (int i=0, n=toIndex-fromIndex; i<n; i++) {
            it.next();
            it.remove();
        }
    }

    /**
     * The number of times this list has been <i>structurally modified</i>.
     * Structural modifications are those that change the size of the
     * list, or otherwise perturb it in such a fashion that iterations in
     * progress may yield incorrect results.
     *
     * <p>This field is used by the iterator and list iterator implementation
     * returned by the {@code iterator} and {@code listIterator} methods.
     * If the value of this field changes unexpectedly, the iterator (or list
     * iterator) will throw a {@code ConcurrentModificationException} in
     * response to the {@code next}, {@code remove}, {@code previous},
     * {@code set} or {@code add} operations.  This provides
     * <i>fail-fast</i> behavior, rather than non-deterministic behavior in
     * the face of concurrent modification during iteration.
     *
     * <p><b>Use of this field by subclasses is optional.</b> If a subclass
     * wishes to provide fail-fast iterators (and list iterators), then it
     * merely has to increment this field in its {@code add(int, E)} and
     * {@code remove(int)} methods (and any other methods that it overrides
     * that result in structural modifications to the list).  A single call to
     * {@code add(int, E)} or {@code remove(int)} must add no more than
     * one to this field, or the iterators (and list iterators) will throw
     * bogus {@code ConcurrentModificationExceptions}.  If an implementation
     * does not wish to provide fail-fast iterators, this field may be
     * ignored.
     */
    protected transient int modCount = 0;

    private void rangeCheckForAdd(int index) {
        if (index < 0 || index > size())
            throw new IndexOutOfBoundsException(outOfBoundsMsg(index));
    }

    private String outOfBoundsMsg(int index) {
        return "Index: "+index+", Size: "+size();
    }
}

class SubList<E> extends AbstractList<E> {
    private final AbstractList<E> l;
    private final int offset;
    private int size;

    SubList(AbstractList<E> list, int fromIndex, int toIndex) {
        if (fromIndex < 0)
            throw new IndexOutOfBoundsException("fromIndex = " + fromIndex);
        if (toIndex > list.size())
            throw new IndexOutOfBoundsException("toIndex = " + toIndex);
        if (fromIndex > toIndex)
            throw new IllegalArgumentException("fromIndex(" + fromIndex +
                                               ") > toIndex(" + toIndex + ")");
        l = list;
        offset = fromIndex;
        size = toIndex - fromIndex;
        this.modCount = l.modCount;
    }

    public E set(int index, E element) {
        rangeCheck(index);
        checkForComodification();
        return l.set(index+offset, element);
    }

    public E get(int index) {
        rangeCheck(index);
        checkForComodification();
        return l.get(index+offset);
    }

    public int size() {
        checkForComodification();
        return size;
    }

    public void add(int index, E element) {
        rangeCheckForAdd(index);
        checkForComodification();
        l.add(index+offset, element);
        this.modCount = l.modCount;
        size++;
    }

    public E remove(int index) {
        rangeCheck(index);
        checkForComodification();
        E result = l.remove(index+offset);
        this.modCount = l.modCount;
        size--;
        return result;
    }

    protected void removeRange(int fromIndex, int toIndex) {
        checkForComodification();
        l.removeRange(fromIndex+offset, toIndex+offset);
        this.modCount = l.modCount;
        size -= (toIndex-fromIndex);
    }

    public boolean addAll(Collection<? extends E> c) {
        return addAll(size, c);
    }

    public boolean addAll(int index, Collection<? extends E> c) {
        rangeCheckForAdd(index);
        int cSize = c.size();
        if (cSize==0)
            return false;

        checkForComodification();
        l.addAll(offset+index, c);
        this.modCount = l.modCount;
        size += cSize;
        return true;
    }

    public Iterator<E> iterator() {
        return listIterator();
    }

    public ListIterator<E> listIterator(final int index) {
        checkForComodification();
        rangeCheckForAdd(index);

        return new ListIterator<E>() {
            private final ListIterator<E> i = l.listIterator(index+offset);

            public boolean hasNext() {
                return nextIndex() < size;
            }

            public E next() {
                if (hasNext())
                    return i.next();
                else
                    throw new NoSuchElementException();
            }

            public boolean hasPrevious() {
                return previousIndex() >= 0;
            }

            public E previous() {
                if (hasPrevious())
                    return i.previous();
                else
                    throw new NoSuchElementException();
            }

            public int nextIndex() {
                return i.nextIndex() - offset;
            }

            public int previousIndex() {
                return i.previousIndex() - offset;
            }

            public void remove() {
                i.remove();
                SubList.this.modCount = l.modCount;
                size--;
            }

            public void set(E e) {
                i.set(e);
            }

            public void add(E e) {
                i.add(e);
                SubList.this.modCount = l.modCount;
                size++;
            }
        };
    }

    public List<E> subList(int fromIndex, int toIndex) {
        return new SubList<E>(this, fromIndex, toIndex);
    }

    private void rangeCheck(int index) {
        if (index < 0 || index >= size)
            throw new IndexOutOfBoundsException(outOfBoundsMsg(index));
    }

    private void rangeCheckForAdd(int index) {
        if (index < 0 || index > size)
            throw new IndexOutOfBoundsException(outOfBoundsMsg(index));
    }

    private String outOfBoundsMsg(int index) {
        return "Index: "+index+", Size: "+size;
    }

    private void checkForComodification() {
        if (this.modCount != l.modCount)
            throw new ConcurrentModificationException();
    }
}

class RandomAccessSubList<E> extends SubList<E> implements RandomAccess {
    RandomAccessSubList(AbstractList<E> list, int fromIndex, int toIndex) {
        super(list, fromIndex, toIndex);
    }

    public List<E> subList(int fromIndex, int toIndex) {
        return new RandomAccessSubList<E>(this, fromIndex, toIndex);
    }
}
package org.pcollections;

import java.util.AbstractSequentialList;
import java.util.Collection;
import java.util.Iterator;
import java.util.ListIterator;



/**
 *
 * A simple persistent stack of non-null values.
 * <p>
 * This implementation is thread-safe (assuming Java's AbstractSequentialList is thread-safe),
 * although its iterators may not be.
 *
 * @author harold
 *
 * @param <E>
 */
public final class ConsPStack<E> extends AbstractSequentialList<E> implements PStack<E> {
//// STATIC FACTORY METHODS ////
	private static final ConsPStack<Object> EMPTY = new ConsPStack<Object>();

	/**
	 * @param <E>
	 * @return an empty stack
	 */
	@SuppressWarnings("unchecked")
	public static <E> ConsPStack<E> empty() {
		return (ConsPStack<E>)EMPTY; }

	/**
	 * @param <E>
	 * @param e
	 * @return empty().plus(e)
	 */
	public static <E> ConsPStack<E> singleton(final E e) {
		return ConsPStack.<E>empty().plus(e); }

	/**
	 * @param <E>
	 * @param list
	 * @return a stack consisting of the elements of list in the order of list.iterator()
	 */
	@SuppressWarnings("unchecked")
	public static <E> ConsPStack<E> from(final Collection<? extends E> list) {
		if(list instanceof ConsPStack)
			return (ConsPStack<E>)list; //(actually we only know it's ConsPStack<? extends E>)
									// but that's good enough for an immutable
									// (i.e. we can't mess someone else up by adding the wrong type to it)
		return ConsPStack.<E>from(list.iterator());
	}

	private static <E> ConsPStack<E> from(final Iterator<? extends E> i) {
		if(!i.hasNext()) return empty();
		E e = i.next();
		return ConsPStack.<E>from(i).plus(e);
	}


//// PRIVATE CONSTRUCTORS ////
	private final E first; private final ConsPStack<E> rest;
	private final int size;
	// not externally instantiable (or subclassable):
	private ConsPStack() { // EMPTY constructor
		if(EMPTY!=null)
			throw new RuntimeException("empty constructor should only be used once");
		size = 0; first=null; rest=null;
	}
	private ConsPStack(final E first, final ConsPStack<E> rest) {
		this.first = first; this.rest = rest;

		size = 1 + rest.size;
	}


//// REQUIRED METHODS FROM AbstractSequentialList ////
	@Override
	public int size() {
		return size; }

	@Override
	public ListIterator<E> listIterator(final int index) {
		if(index<0 || index>size) throw new IndexOutOfBoundsException();

		return new ListIterator<E>() {
			int i = index;
			ConsPStack<E> next = subList(index);

			public boolean hasNext() {
				return next.size>0; }
			public boolean hasPrevious() {
				return i>0; }
			public int nextIndex() {
				return index; }
			public int previousIndex() {
				return index-1; }
			public E next() {
				E e = next.first;
				next = next.rest;
				return e;
			}
			public E previous() {
				System.err.println("ConsPStack.listIterator().previous() is inefficient, don't use it!");
				next = subList(index-1); // go from beginning...
				return next.first;
			}

			public void add(final E o) {
				throw new UnsupportedOperationException(); }
			public void remove() {
				throw new UnsupportedOperationException(); }
			public void set(final E o) {
				throw new UnsupportedOperationException(); }
		};
	}


//// OVERRIDDEN METHODS FROM AbstractSequentialList ////
	@Override
	public ConsPStack<E> subList(final int start, final int end) {
		if(start<0 || end>size || start>end)
			throw new IndexOutOfBoundsException();
		if(end==size) // want a substack
			return subList(start); // this is faster
		if(start==end) // want nothing
			return empty();
		if(start==0) // want the current element
			return new ConsPStack<E>(first, rest.subList(0, end-1));
		// otherwise, don't want the current element:
		return rest.subList(start-1, end-1);
	}


//// IMPLEMENTED METHODS OF PStack ////
	public ConsPStack<E> plus(final E e) {
		return new ConsPStack<E>(e, this);
	}

	public ConsPStack<E> plusAll(final Collection<? extends E> list) {
		ConsPStack<E> result = this;
		for(E e : list)
			result = result.plus(e);
		return result;
	}

	public ConsPStack<E> plus(final int i, final E e) {
		if(i<0 || i>size)
			throw new IndexOutOfBoundsException();
		if(i==0) // insert at beginning
			return plus(e);
		return new ConsPStack<E>(first, rest.plus(i-1, e));
	}

	public ConsPStack<E> plusAll(final int i, final Collection<? extends E> list) {
		// TODO inefficient if list.isEmpty()
		if(i<0 || i>size)
			throw new IndexOutOfBoundsException();
		if(i==0)
			return plusAll(list);
		return new ConsPStack<E>(first, rest.plusAll(i-1, list));
	}

	public ConsPStack<E> minus(final Object e) {
		if(size==0)
			return this;
		if(first.equals(e)) // found it
			return rest; // don't recurse (only remove one)
		// otherwise keep looking:
		ConsPStack<E> newRest = rest.minus(e);
		if(newRest==rest) return this;
		return new ConsPStack<E>(first, newRest);
	}

	public ConsPStack<E> minus(final int i) {
		if (i < 0 || i >= size)
			throw new IndexOutOfBoundsException("Index: " + i + "; size: " + size);
		else if (i == 0)
			return rest;
		else return new ConsPStack<E>(first, rest.minus(i-1));
	}

	public ConsPStack<E> minusAll(final Collection<?> list) {
		if(size==0)
			return this;
		if(list.contains(first)) // get rid of current element
			return rest.minusAll(list); // recursively delete all
		// either way keep looking:
		ConsPStack<E> newRest = rest.minusAll(list);
		if(newRest==rest) return this;
		return new ConsPStack<E>(first, newRest);
	}

	public ConsPStack<E> with(final int i, final E e) {
		if(i<0 || i>=size)
			throw new IndexOutOfBoundsException();
		if(i==0) {
			if(first.equals(e)) return this;
			return new ConsPStack<E>(e, rest);
		}
		ConsPStack<E> newRest = rest.with(i-1, e);
		if(newRest==rest) return this;
		return new ConsPStack<E>(first, newRest);
	}

	public ConsPStack<E> subList(final int start) {
		if(start<0 || start>size)
			throw new IndexOutOfBoundsException();
		if(start==0)
			return this;
		return rest.subList(start-1);
	}
}
"""
