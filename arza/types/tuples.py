from arza.types.root import W_Hashable, W_Root
from arza.runtime import error
from arza.types import api, space, plist
from arza.misc import platform

"""
 @jit.look_inside_iff(lambda self, _1: _unroll_condition(self))
    def descr_hash(self, space):
        mult = 1000003
        x = 0x345678
        z = len(self.wrappeditems)
        for w_item in self.wrappeditems:
            y = space.hash_w(w_item)
            x = (x ^ y) * mult
            z -= 1
            mult += 82520 + z + z
        x += 97531
        return space.wrap(intmask(x))

    def descr_eq(self, space, w_other):
        if not isinstance(w_other, W_AbstractTupleObject):
            return space.w_NotImplemented
        return self._descr_eq(space, w_other)

    @jit.look_inside_iff(_unroll_condition_cmp)
    def _descr_eq(self, space, w_other):
        items1 = self.wrappeditems
        items2 = w_other.tolist()
        lgt1 = len(items1)
        lgt2 = len(items2)
        if lgt1 != lgt2:
            return space.w_False
        for i in range(lgt1):
            item1 = items1[i]
            item2 = items2[i]
            if not space.eq_w(item1, item2):
                return space.w_False
        return space.w_True
"""


class W_Unit(W_Root):
    def _hash_(self):
        return 0x345678

    def _clone_(self):
        return self

    def __iter__(self):
        raise StopIteration()

    def __getitem__(self, item):
        raise RuntimeError("Unit has no elements")

    def _type_(self, process):
        return process.std.types.Tuple

    def _contains_(self, key):
        return False

    def _at_(self, index):
        return space.newvoid()

    def _at_index_(self, i):
        return space.newvoid()

    def _get_index_(self, obj):
        return platform.absent_index()

    def _length_(self):
        return 0

    def _equal_(self, other):
        if isinstance(other, W_Unit):
            return True
        return False

    def _to_string_(self):
        return "()"

    def _to_repr_(self):
        return self._to_string_()

    def to_l(self):
        return []


class W_Tuple(W_Hashable):
    def __init__(self, items):
        assert isinstance(items, list)
        W_Hashable.__init__(self)
        self.elements = items
        self.length = len(self.elements)

    def __iter__(self):
        for v in self.elements:
            yield v

    def __len__(self):
        return len(self.elements)

    def __getitem__(self, item):
        return self.elements[item]

    def __getslice__(self, start, end):
        return W_Tuple(self.elements[start:end])

    def _compute_hash_(self):
        from arza.misc.platform import rarithmetic
        x = 0x345678
        for item in self.elements:
            y = api.hash_i(item)
            x = rarithmetic.intmask((1000003 * x) ^ y)
        return x

    def _type_(self, process):
        return process.std.types.Tuple

    def _clone_(self):
        return W_Tuple(self.elements)

    def _contains_(self, key):
        for item in self.elements:
            if api.equal_b(item, key):
                return True
        return False

    def _at_(self, index):
        from arza.types.space import newvoid, isint
        assert isint(index)
        try:
            el = self.elements[api.to_i(index)]
        except IndexError:
            return newvoid()

        return el

    def _at_index_(self, i):
        return self.elements[i]

    def _get_index_(self, obj):
        try:
            return self.elements.index(obj)
        except ValueError:
            return -1

    def _length_(self):
        return len(self.elements)

    def _equal_(self, other):
        from arza.types import space
        if not space.istuple(other):
            return False

        if self._length_() != other._length_():
            return False

        for el1, el2 in zip(self.elements, other.elements):
            if not api.equal_b(el1, el2):
                return False

        return True

    def _to_string_(self):
        data = [v._to_string_() for v in self.elements]
        repr = ", ".join(data)

        if self._length_() == 1:
            return "(%s,)" % repr
        return "(%s)" % repr

    def _to_repr_(self):
        return self._to_string_()

    def __repr__(self):
        return self._to_string_()

    def to_l(self):
        return self.elements


def type_check(t):
    error.affirm_type(t, space.istuple)


def concat(tupl1, tupl2):
    if space.islist(tupl1):
        tupl1 = plist.to_tuple(tupl1)
    elif space.islist(tupl2):
        tupl2 = plist.to_tuple(tupl2)

    type_check(tupl1)
    type_check(tupl2)
    if space.isunit(tupl1):
        return tupl2
    if space.isunit(tupl2):
        return tupl1

    return W_Tuple(tupl1.elements + tupl2.elements)


def prepend(tupl, val):
    type_check(tupl)
    if space.isunit(tupl):
        return space.newtuple([val])

    return W_Tuple([val] + tupl.elements)


def to_list(t):
    type_check(t)
    if space.isrealtuple(t):
        return space.newlist(t.elements)
    else:
        return plist.empty()


def slice(t, first, last):
    error.affirm_type(t, space.isrealtuple)
    assert isinstance(first, int)
    assert isinstance(last, int)
    if first < 0:
        error.throw_2(error.Errors.SLICE_ERROR, space.newstring(u"First index < 0"), space.newint(first))
    if first >= last:
        error.throw_3(error.Errors.SLICE_ERROR, space.newstring(u"First index >= Last index"),
                      space.newint(first), space.newint(last))
    if last >= t.length:
        error.throw_2(error.Errors.SLICE_ERROR, space.newstring(u"Last index too big"), space.newint(last))
    return W_Tuple(t.elements[first:last])


def take(t, count):
    error.affirm_type(t, space.isrealtuple)
    assert isinstance(count, int)
    if count < 0:
        error.throw_2(error.Errors.SLICE_ERROR, space.newstring(u"Count < 0"), space.newint(count))

    if count >= t.length:
        error.throw_2(error.Errors.SLICE_ERROR, space.newstring(u"Count too big"), space.newint(count))

    return W_Tuple(t.elements[:count])


def drop(t, count):
    error.affirm_type(t, space.istuple)
    if space.isunit(t):
        return t
    assert isinstance(count, int)
    if count < 0:
        error.throw_2(error.Errors.SLICE_ERROR, space.newstring(u"Count < 0"), space.newint(count))

    if count >= t.length:
        return space.newunit()
        # error.throw_2(error.Errors.SLICE_ERROR, space.newstring(u"Count too big"), space.newint(count))
    return W_Tuple(t.elements[count:])


# USED ONLY IN COMPILER FOR REPLACING @ in map modify expression
# IT JUST VERY HARD IN CURRENT DESIGN TO REPLACE EXPRESSION
def modify_tuple(t, index, val):
    t.elements[index] = val


def types_tuple(process, t):
    error.affirm_type(t, space.isrealtuple)
    types = []
    for el in t.elements:
        _type = api.get_type(process, el)
        types.append(_type)

    return W_Tuple(types)
