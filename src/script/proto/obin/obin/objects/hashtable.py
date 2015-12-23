from obin.objects.space import newundefined, isundefined, isany
from obin.objects import api

MINSIZE = 8
PERTURB_SHIFT = 5

NOT_FOUND = -1


class HashTable:
    def __init__(self, minsize, perturb_shift):
        self._minsize = minsize
        self._perturb_shift = perturb_shift
        self._backing = None
        self._build(self._minsize)

    def _lookup_index(self, key):
        backing = self._backing
        for i in self._indices(key, len(backing)):
            value = backing[i]
            if isundefined(value[0]):
                return i

            if api.n_equal(value[0], key):
                return i

        return NOT_FOUND

    def get(self, key):
        # Performs a lookup to find the index and value of the key
        # in the backing structure
        i = self._lookup_index(key)

        kv_pair = self._backing[i]
        if isundefined(kv_pair[0]):
            raise KeyError()
        return kv_pair[1]

    def is_empty_pair(self, kv_pair):
        return isundefined(kv_pair[0])

    def set(self, key, value):
        assert isany(key)
        assert not isundefined(key)
        assert isinstance(value, int)
        """
        Sets the value of the Hashmap at the key. It resizes the backing
        structure if the utilization of the Hashmap is > ~ 2/3
        """
        i = self._lookup_index(key)
        kv_pair = self._backing[i]
        self._backing[i] = (key, value)
        if self.is_empty_pair(kv_pair):
            self._used += 1

        size = len(self._backing)
        utilization = self._used / size
        if utilization > 0.67:
            self._resize(self._incr_size(size))

    def contains(self, key):
        """key in x => boolean
        Returns true if key is contained in the Hashmap.
        """
        i = self._lookup_index(key)
        return i != NOT_FOUND

    def keys(self):
        l = []
        for kv_pair in self._backing:
            if kv_pair and not isundefined(kv_pair[0]):
                l.append(kv_pair[0])
        return l

    def __iter__(self):
        """iter(x) => Generator
        Returns a generator that iterates over the key value tuples in
        the Hashmap.
        """
        for kv_pair in self._backing:
            if kv_pair and not isundefined(kv_pair[0]):
                yield kv_pair[0]

    def items(self):
        """iter(x) => Generator
        Returns a generator that iterates over the key value tuples in
        the Hashmap.
        """
        for kv_pair in self._backing:
            if kv_pair and not isundefined(kv_pair[0]):
                yield kv_pair[0], kv_pair[1]

    def copy(self):
        h = newhashtable()
        for kv_pair in self._backing:
            if not self.is_empty_pair(kv_pair):
                h.set(kv_pair[0], kv_pair[1])
        return h

    def length(self):
        """len(x) => Integer
        Returns the number of key value tuples stored in the Hashmap.
        """
        return self._used - self._deleted

    # def delete(self, key):
    #     """del(x[key])
    #     Sets the key in the Hashmap to absent, releasing the original
    #     item. It resizes the backing structure if the utilization of
    #     the Hashmap is < ~ 1/6
    #     """
    #     i, kv_pair = self.get(key)
    #     if kv_pair and not kv_pair.value is Hashmap.absent:
    #         self._backing[i] = (key, Hashmap.absent)
    #         self._deleted += 1
    #
    #         size = len(self._backing)
    #         utilization = (self._used - self._deleted)/size
    #         if utilization < 0.16:
    #             self._resize(self._decr_size(size))
    #     else:
    #         raise KeyError('no such item!')

    def _indices(self, key, size):
        # Produces the list of indices that the Hashmap uses in 
        # open addressing
        #
        # Based on:
        # http://svn.python.org/view/python/trunk/Objects/dictobject.c?view=markup
        j = perturb = api.n_hash(key)
        for _ in range(size):
            j %= size
            yield j
            j = 5 * j + 1 + perturb
            perturb >>= self._perturb_shift

    def _resize(self, new_size):
        # Resizes the backing structure if new size is different
        if new_size != len(self._backing):
            old_backing = self._backing[:]
            self._build(new_size, old_backing)

    def _build(self, size, init=None):
        # Build a new backing structure given a old list of (possibly None)
        # key value tuples
        if not init:
            init = []
        self._backing = [(newundefined(), NOT_FOUND)] * size
        self._used = 0
        self._deleted = 0
        for kv_pair in init:
            if not self.is_empty_pair(kv_pair):
                self.set(kv_pair[0], kv_pair[1])

    def _incr_size(self, size):
        return size * 2

    def _decr_size(self, size):
        return max(self._minsize, size // 2)


def newhashtable():
    return HashTable(MINSIZE, PERTURB_SHIFT)
