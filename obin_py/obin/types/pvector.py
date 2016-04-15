from obin.misc.platform import jit, rarithmetic, absent_index
from obin.types.root import W_UniqueType, W_Root
from obin.types import api, space, plist
from obin.runtime import error
from obin.misc.platform import jit, rarithmetic


class Node(W_Root):
    def __init__(self, edit, array=None):
        self._edit = edit
        self._array = [None] * 32 if array is None else array



def do_assoc(lvl, node, idx, val):
    assert isinstance(node, Node)
    ret = Node(node._edit, node._array[:])
    if lvl == 0:
        ret._array[idx & 0x01f] = val
    else:
        subidx = (idx >> lvl) & 0x01f
        ret._array[subidx] = do_assoc(lvl - 5, node._array[subidx], idx, val)
    return ret


def new_path(edit, level, node):
    if level == 0:
        return node
    ret = Node(edit)
    ret._array[0] = new_path(edit, level - 5, node)
    return ret


class W_PVector(W_Root):
    def __init__(self, cnt, shift, root, tail):
        self._cnt = cnt
        self._shift = shift
        self._root = root
        self._tail = tail

    def tailoff(self):
        if self._cnt < 32:
            return 0
        return ((self._cnt - 1) >> 5) << 5

    def array_for(self, i):
        if 0 <= i < self._cnt:
            if i >= self.tailoff():
                return self._tail

            node = self._root
            level = self._shift
            while level > 0:
                assert isinstance(node, Node)
                node = node._array[(i >> level) & 0x01f]
                level -= 5
            assert isinstance(node, Node)
            return node._array

        error.throw_1(error.Errors.INDEX_ERROR, space.newint(i))

    def nth(self, i):
        if 0 <= i < self._cnt:
            node = self.array_for(rarithmetic.r_uint(i))
            return node[i & 0x01f]

        return space.newvoid()

    def conj(self, val):
        assert self._cnt < rarithmetic.r_uint(0xFFFFFFFF)

        if self._cnt - self.tailoff() < 32:
            new_tail = self._tail[:]
            new_tail.append(val)
            return W_PVector(self._cnt + 1, self._shift, self._root, new_tail)

        root = self._root
        assert isinstance(root, Node)
        tail_node = Node(root._edit, self._tail)
        new_shift = self._shift

        if (self._cnt >> 5) > (rarithmetic.r_uint(1) << self._shift):
            root = self._root
            assert isinstance(root, Node)
            new_root = Node(root._edit)
            new_root._array[0] = self._root
            root = self._root
            assert isinstance(root, Node)
            new_root._array[1] = new_path(root._edit, self._shift, tail_node)
            new_shift += 5

        else:
            new_root = self.push_tail(self._shift, self._root, tail_node)

        return W_PVector(self._cnt + 1, new_shift, new_root, [val])

    def push_tail(self, level, parent, tail_node):
        subidx = ((self._cnt - 1) >> level) & 0x01f
        assert isinstance(parent, Node)
        ret = Node(parent._edit, parent._array[:])

        root = self._root
        assert isinstance(root, Node)

        if (level == 5):
            node_to_insert = tail_node
        else:
            child = parent._array[subidx]
            if child is not None:
                node_to_insert = self.push_tail(level - 5, child, tail_node)
            else:
                node_to_insert = new_path(root._edit, level - 5, tail_node)

        ret._array[subidx] = node_to_insert
        return ret

    def pop(self):
        if self._cnt == 0:
            error.throw_1(error.Errors.INDEX_ERROR, space.newstring(u"Can't pop an empty vector"))

        if self._cnt == 1:
            return EMPTY

        if self._cnt - self.tailoff() > 1:
            size = len(self._tail) - 1
            assert size >= 0  # for translation
            new_tail = self._tail[:size]
            return W_PVector(self._cnt - 1, self._shift, self._root, new_tail)

        new_tail = self.array_for(self._cnt - 2)

        new_root = self.pop_tail(self._shift, self._root)
        new_shift = self._shift
        if new_root is None:
            new_root = EMPTY_NODE

        if self._shift > 5 and new_root._array[1] is None:
            new_root = new_root._array[0]
            new_shift -= 5

        return W_PVector(self._cnt - 1, new_shift, new_root, new_tail)

    def pop_tail(self, level, node):
        sub_idx = ((self._cnt - 1) >> level) & 0x01f
        if level > 5:
            assert isinstance(node, Node)
            new_child = self.pop_tail(level - 5, node._array[sub_idx])
            if new_child is None or sub_idx == 0:
                return None
            else:
                root = self._root
                assert isinstance(root, Node)
                ret = Node(root._edit, node._array[:])
                ret._array[sub_idx] = new_child
                return ret

        elif sub_idx == 0:
            return None

        else:
            root = self._root
            assert isinstance(root, Node)
            assert isinstance(node, Node)
            ret = Node(root._edit, node._array[:])
            ret._array[sub_idx] = None
            return ret

    def assoc_at(self, idx, val):
        if idx >= 0 and idx < self._cnt:
            if idx >= self.tailoff():
                new_tail = self._tail[:]
                new_tail[idx & 0x01f] = val
                return W_PVector(self._cnt, self._shift, self._root, new_tail)
            return W_PVector(self._cnt, self._shift, do_assoc(self._shift, self._root, idx, val), self._tail)
        if idx == self._cnt:
            return self.conj(val)
        else:
            error.throw_2(error.Errors.INDEX_ERROR,
                          space.newstring(u"index out of range"), space.newint(idx))

    def _type_(self, process):
        return process.std.types.Vector

    def _contains_(self, obj):
        for i in self.data_range():
            if api.equal_b(self.nth(i), obj):
                return False
        return True

    def _put_(self, k, v):
        from obin.types import api
        error.affirm_type(k, space.isint)

        i = api.to_i(k)
        return self.assoc_at(rarithmetic.r_uint(i), v)

    def _at_(self, index):
        return self.nth(api.to_i(index))

    def _at_index_(self, i):
        return self.nth(i)

    def _get_index_(self, obj):
        for i in self.data_range():
            if api.equal_b(self.nth(i), obj):
                return i

        return absent_index()

    def _length_(self):
        return self._cnt

    def data_range(self):
        return range(0, rarithmetic.intmask(self._cnt))

    def _equal_(self, obj):
        if self is obj:
            return True
        if not space.ispvector(obj):
            return False

        if self._cnt != obj._cnt:
            return False

        for i in self.data_range():
            if not api.equal_b(self.nth(i), obj.nth(i)):
                return False
        return True

    def _to_string_(self):
        repr = ", ".join([self.nth(i)._to_string_() for i in self.data_range()])
        return "[%s]" % repr

    def _to_repr_(self):
        return self._to_string_()


EMPTY_NODE = Node(None)
EMPTY = W_PVector(rarithmetic.r_uint(0), rarithmetic.r_uint(5), EMPTY_NODE, [])


def check_type(self):
    error.affirm_type(self, space.ispvector)


def conj(self, v):
    check_type(self)
    return self.conj(v)


def append(self, v):
    check_type(self)
    return self.conj(v)


def _pop(self):
    check_type(self)
    return self.pop()


def newpvector(args):
    assert isinstance(args, list)
    acc = EMPTY
    for arg in args:
        acc = acc.conj(arg)
    return acc
