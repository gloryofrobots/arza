from capy.types.root import W_Hashable, W_Root
from capy.runtime import error
from capy.runtime.stack import Stack
from capy.types import api, space, plist
from capy.misc import platform


class W_Arguments(W_Root):
    def __init__(self, stack, pointer, length):
        assert isinstance(length, int)
        assert length > 0
        assert length < stack.size()
        assert isinstance(stack, Stack)

        assert isinstance(pointer, int)
        assert pointer > 0
        assert pointer <= stack.pointer()
        self.pointer = pointer
        self.start = pointer - length
        self.stack = stack
        self.length = length

    def to_l(self):
        l = [self.get(i) for i in range(self.length)]
        return l

    def get(self, i):
        index = self.start + i
        return self.stack.get(index)

    def _type_(self, process):
        return process.std.classes.Tuple

    def _has_(self, obj):
        i = self._get_index_(obj)
        return platform.is_absent_index(i)

    def _at_(self, index):
        from capy.types.space import newvoid, isint
        assert isint(index)
        i = api.to_i(index)
        if i < 0 or i > self.length - 1:
            return newvoid()

        return self.get(i)

    def _at_index_(self, i):
        return self.get(i)

    def _get_index_(self, obj):
        for i in range(self.length):
            item = self.get(i)
            if api.equal_b(item, obj):
                return i
        return platform.absent_index()

    def _length_(self):
        return self.length

    # def _equal_(self, other):
    #     from arza.types import space
    #     if not space.istuple(other):
    #         return False
    #
    #     if self._length_() != other._length_():
    #         return False
    #
    #     for el1, el2 in zip(self.elements, other.elements):
    #         if not api.equal_b(el1, el2):
    #             return False
    #
    #     return True

    def _to_string_(self):
        repr = ", ".join([v._to_string_() for v in self.to_l()])
        return "<%s>" % repr

    def _to_repr_(self):
        return self._to_string_()

def type_check(t):
    error.affirm_type(t, space.isarray)


def to_list(t):
    type_check(t)
    return space.newlist(t.elements)


def slice(t, first, last):
    error.affirm_type(t, space.isarguments)
    assert isinstance(first, int)
    assert isinstance(last, int)
    if last >= t.length:
        error.throw_2(error.Errors.SLICE_ERROR, space.newstring(u"Invalid slice last index"), space.newint(last))

    return W_Arguments(t.stack, t.pointer - first, last)


def take(t, count):
    error.affirm_type(t, space.isarguments)
    if count >= t.length:
        error.throw_2(error.Errors.SLICE_ERROR, space.newstring(u"Can not take so much items"), space.newint(count))

    assert isinstance(count, int)
    return W_Arguments(t.stack, t.pointer, count)


def drop(t, count):
    error.affirm_type(t, space.isarguments)
    assert isinstance(count, int)
    if count >= t.length:
        error.throw_2(error.Errors.SLICE_ERROR, space.newstring(u"Can not drop so much items"), space.newint(count))

    return W_Arguments(t.stack, t.pointer - count, t.length)
