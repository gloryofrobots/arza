from rpython.rlib.rarithmetic import r_int, r_uint, intmask
import rpython.rlib.jit as jit
from obin.types.root import W_UniqueType, W_Any
from obin.types import api, space, vector
from obin.runtime import error

MASK_32 = r_uint(0xFFFFFFFF)

NOT_FOUND = W_UniqueType()


class Box:
    def __init__(self):
        self._val = None


def _hash(key):
    return api.n_hash(key) & MASK_32


def _tostring(pair, vec):
    key = api.at(pair, space.newint(0))
    value = api.at(pair, space.newint(1))
    if space.isstring(value):
        tpl = u'%s = "%s"'
    else:
        tpl = u'%s = %s'

    repr = tpl % (api.to_u(key), api.to_u(value))
    vec.to_l().append(repr)
    return vec


def _equal(pair, other):
    key = api.at(pair, space.newint(0))
    value = api.at(pair, space.newint(1))
    value2 = api.at(other, key)
    if not api.n_equal(value, value2):
        return error.throw_2(error.Errors.KEY, key, other)
    return other


class W_PMap(W_Any):
    def __init__(self, cnt, root):
        self._cnt = cnt
        self._root = root

    def _tostring_(self):
        lst = self.to_l()
        repr = u"{%s}" % u", ".join(lst)
        return str(repr)

    def _behavior_(self, process):
        return process.std.behaviors.Map

    def _length_(self):
        return self._cnt

    def _put_(self, key, val):
        added_leaf = Box()

        new_root = (BitmapIndexedNode_EMPTY if self._root is None else self._root) \
            .assoc_inode(r_uint(0), _hash(key), key, val, added_leaf)

        if new_root is self._root:
            return self

        return W_PMap(self._cnt if added_leaf._val is None else self._cnt + 1, new_root)

    def _at_(self, key):
        if self._root is None:
            return space.newnil()

        return self._root.find(r_uint(0), _hash(key), key)

    def _delete_(self, key):
        if self._root is None:
            return self

        new_root = self._root.without_inode(0, _hash(key), key)

        if new_root is self._root:
            return self
        return W_PMap(self._cnt - 1, new_root)

    def _equal_(self, other):
        if not space.ispmap(other):
            return False
        try:
            self._root.reduce(_equal, other)
            return True
        except error.ObinError as e:
            return False

    def to_l(self):
        pairs = self._root.reduce(_tostring, space.newvector([]))
        lst = pairs.to_l()
        return lst


class INode(W_Any):
    def assoc_inode(self, shift, hash_val, key, val, added_leaf):
        pass

    def find(self, shift, hash_val, key):
        pass

    def without(self, shift, hash, key):
        pass

    def reduce(self, f, init):
        pass


def mask(hash, shift):
    return (hash >> shift) & 0x01f


def bitpos(hash, shift):
    return (1 << mask(hash, shift)) & MASK_32


class BitmapIndexedNode(INode):
    def __init__(self, edit, bitmap, array):
        self._edit = edit
        self._bitmap = bitmap
        self._array = array

    def index(self, bit):
        return bit_count(self._bitmap & (bit - 1))

    def reduce(self, f, init):
        for x in range(0, len(self._array), 2):
            key_or_none = self._array[x]
            val_or_node = self._array[x + 1]
            if key_or_none is None and val_or_node is not None:
                init = val_or_node.reduce(f, init)
            else:
                init = f(space.newtuple([key_or_none, val_or_node]), init)
        return init

    def assoc_inode(self, shift, hash_val, key, val, added_leaf):
        bit = bitpos(hash_val, shift)
        idx = self.index(bit)

        if (self._bitmap & bit) != 0:
            key_or_null = self._array[2 * idx]
            val_or_node = self._array[2 * idx + 1]

            if key_or_null is None:
                assert isinstance(val_or_node, INode)
                n = val_or_node.assoc_inode(shift + 5, hash_val & MASK_32, key, val, added_leaf)
                if n is val_or_node:
                    return self
                return BitmapIndexedNode(None, self._bitmap, clone_and_set(self._array, 2 * idx + 1, n))

            if api.n_equal(key, key_or_null):
                if val is val_or_node:
                    return self
                return BitmapIndexedNode(None, self._bitmap, clone_and_set(self._array, 2 * idx + 1, val))

            added_leaf._val = added_leaf
            return BitmapIndexedNode(None, self._bitmap,
                                     clone_and_set2(self._array,
                                                    2 * idx, None,
                                                    2 * idx + 1,
                                                    create_node(shift + 5, key_or_null, val_or_node, hash_val, key,
                                                                val)))
        else:
            n = bit_count(self._bitmap)
            if n >= 16:
                nodes = [None] * 32
                jdx = mask(hash_val, shift)
                nodes[jdx] = BitmapIndexedNode_EMPTY.assoc_inode(shift + 5, hash_val, key, val, added_leaf)
                j = 0

                for i in range(32):
                    if (self._bitmap >> i) & 1 != 0:
                        if self._array[j] is None:
                            nodes[i] = self._array[j + 1]
                        else:
                            nodes[i] = BitmapIndexedNode_EMPTY.assoc_inode(shift + 5, api.n_hash(self._array[j]),
                                                                           self._array[j], self._array[j + 1],
                                                                           added_leaf)
                        j += 2

                return ArrayNode(None, n + 1, nodes)
            else:
                new_array = [None] * (2 * (n + 1))
                list_copy(self._array, 0, new_array, 0, 2 * idx)
                new_array[2 * idx] = key
                added_leaf._val = added_leaf
                new_array[2 * idx + 1] = val
                list_copy(self._array, 2 * idx, new_array, 2 * (idx + 1), 2 * (n - idx))
                return BitmapIndexedNode(None, self._bitmap | bit, new_array)

    def find(self, shift, hash_val, key):
        bit = bitpos(hash_val, shift)
        if (self._bitmap & bit) == 0:
            return space.newnil()

        idx = self.index(bit)
        key_or_null = self._array[2 * idx]
        val_or_node = self._array[2 * idx + 1]
        if key_or_null is None:
            return val_or_node.find(shift + 5, hash_val, key)
        if api.n_equal(key, key_or_null):
            return val_or_node

        return space.newnil()

    def without_inode(self, shift, hash, key):
        bit = bitpos(hash, shift)
        if self._bitmap & bit == 0:
            return self

        idx = self.index(bit)
        key_or_none = self._array[2 * idx]
        val_or_node = self._array[2 * idx + 1]

        if key_or_none is None:
            n = val_or_node.without_inode(shift + 5, hash, key)
            if n is val_or_node:
                return self
            if n is not None:
                return BitmapIndexedNode(None, self._bitmap, clone_and_set(self._array, 2 * idx + 1, n))

            if self._bitmap == bit:
                return None

            return BitmapIndexedNode(None, self._bitmap ^ bit, remove_pair(self._array, idx))

        if api.n_equal(key, key_or_none):
            return BitmapIndexedNode(None, self._bitmap ^ bit, remove_pair(self._array, idx))

        return self


BitmapIndexedNode_EMPTY = BitmapIndexedNode(None, r_uint(0), [])


class ArrayNode(INode):
    def __init__(self, edit, cnt, array):
        self._cnt = cnt
        self._edit = edit
        self._array = array

    def reduce(self, f, init):
        for x in range(len(self._array)):
            node = self._array[x]
            if node is not None:
                init = node.reduce(f, init)

        return init

    def assoc_inode(self, shift, hash_val, key, val, added_leaf):
        idx = mask(hash_val, shift)
        node = self._array[idx]
        if node is None:
            return ArrayNode(None, self._cnt + 1, clone_and_set(self._array, idx,
                                                                BitmapIndexedNode_EMPTY.assoc_inode(shift + 5, hash_val,
                                                                                                    key, val,
                                                                                                    added_leaf)))

        n = node.assoc_inode(shift + 5, hash_val, key, val, added_leaf)
        if n is node:
            return self
        return ArrayNode(None, self._cnt, clone_and_set(self._array, idx, n))

    def without_inode(self, shift, hash_val, key):
        idx = r_uint(mask(hash_val, shift))
        node = self._array[idx]
        if node is None:
            return self
        n = node.without_inode(shift + 5, hash_val, key)
        if n is node:
            return self
        if n is None:
            if self._cnt <= 8:  # shrink
                return self.pack(idx)
            return ArrayNode(None, self._cnt - 1, clone_and_set(self._array, idx, n))
        else:
            return ArrayNode(None, self._cnt, clone_and_set(self._array, idx, n))

    def pack(self, idx):
        new_array = [None] * (2 * (self._cnt - 1))
        j = r_uint(1)
        bitmap = r_uint(0)

        i = r_uint(0)
        while i < idx:
            if self._array[i] is not None:
                new_array[j] = self._array[i]
                bitmap |= r_uint(1) << i
                j += 2

            i += 1

        i = r_uint(idx) + 1
        while i < len(self._array):
            if self._array[i] is not None:
                new_array[j] = self._array[i]
                bitmap |= r_uint(1) << i
                j += 2

            i += 1

        return BitmapIndexedNode(None, bitmap, new_array)

    def find(self, shift, hash_val, key):
        idx = mask(hash_val, shift)
        node = self._array[idx]
        if node is None:
            return space.newnil()
        return node.find(shift + 5, hash_val, key)


class HashCollisionNode(INode):
    def __init__(self, edit, hash, array):
        self._hash = hash
        self._edit = edit
        self._array = array

    def reduce(self, f, init):
        for x in range(0, len(self._array), 2):
            key_or_nil = self._array[x]
            if key_or_nil is None:
                continue

            val = self._array[x + 1]
            init = f(space.newtuple([key_or_nil, val]), init)

        return init

    def assoc_inode(self, shift, hash_val, key, val, added_leaf):
        if hash_val == self._hash:
            count = len(self._array)
            idx = self.find_index(key)
            if idx != -1:
                if self._array[idx + 1] == val:
                    return self;
                return HashCollisionNode(None, hash_val, clone_and_set(self._array, r_uint(idx + 1), val))

            new_array = [None] * (count + 2)
            list_copy(self._array, 0, new_array, 0, count)
            new_array[count] = key
            added_leaf._val = added_leaf
            new_array[count + 1] = val
            return HashCollisionNode(self._edit, self._hash, new_array)
        return BitmapIndexedNode(None, bitpos(self._hash, shift), [None, self]) \
            .assoc_inode(shift, hash_val, key, val, added_leaf)

    def find(self, shift, hash_val, key):
        for x in range(0, len(self._array), 2):
            key_or_nil = self._array[x]
            if key_or_nil is not None and api.n_equal(key_or_nil, key):
                return self._array[x + 1]

        return space.newnil()

    def find_index(self, key):
        i = r_int(0)
        while i < len(self._array):
            if api.n_equal(key, self._array[i]):
                return i

            i += 2

        return r_int(-1)

    def without_inode(self, shift, hash, key):
        idx = self.find_index(key)
        if idx == -1:
            return self

        if len(self._array) == 1:
            return None

        return HashCollisionNode(None, self._hash, remove_pair(self._array, r_uint(idx) / 2))


def create_node(shift, key1, val1, key2hash, key2, val2):
    key1hash = api.n_hash(key1) & MASK_32
    if key1hash == key2hash:
        return HashCollisionNode(None, key1hash, [key1, val1, key2, val2])
    added_leaf = Box()
    return BitmapIndexedNode_EMPTY.assoc_inode(shift, key1hash, key1, val1, added_leaf) \
        .assoc_inode(shift, key2hash, key2, val2, added_leaf)


def bit_count(i):
    assert isinstance(i, r_uint)
    i = i - ((i >> 1) & r_uint(0x55555555))
    i = (i & r_uint(0x33333333)) + ((i >> 2) & r_uint(0x33333333))
    return (((i + (i >> 4) & r_uint(0xF0F0F0F)) * r_uint(0x1010101)) & r_uint(0xffffffff)) >> 24


@jit.unroll_safe
def list_copy(from_lst, from_loc, to_list, to_loc, count):
    from_loc = r_uint(from_loc)
    to_loc = r_uint(to_loc)
    count = r_uint(count)

    i = r_uint(0)
    while i < count:
        to_list[to_loc + i] = from_lst[from_loc + i]
        i += 1
    return to_list


@jit.unroll_safe
def clone_and_set(array, i, a):
    clone = [None] * len(array)

    idx = r_uint(0)
    while idx < len(array):
        clone[idx] = array[idx]
        idx += 1

    clone[i] = a
    return clone


@jit.unroll_safe
def clone_and_set2(array, i, a, j, b):
    clone = [None] * len(array)

    idx = r_uint(0)
    while idx < len(array):
        clone[idx] = array[idx]
        idx += 1

    clone[i] = a
    clone[j] = b
    return clone


def remove_pair(array, i):
    new_array = [None] * (len(array) - 2)
    list_copy(array, 0, new_array, 0, 2 * i)
    list_copy(array, 2 * (i + 1), new_array, 2 * i, len(new_array) - (2 * i))
    return new_array


### hook into RT

EMPTY = W_PMap(r_uint(0), None)


def pmap(args):
    assert len(args) & 0x1 == 0, u"hashmap requires even number of args"

    idx = 0
    acc = EMPTY

    while idx < len(args):
        key = args[idx]
        val = args[idx + 1]

        acc = acc._put_(key, val)

        idx += 2

    return acc
