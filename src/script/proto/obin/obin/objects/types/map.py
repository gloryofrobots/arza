from obin.objects import api
from obin.objects.types.root import W_Root, W_Cell
from obin.utils.builtins import is_absent_index, absent_index


# from rpython.rlib.objectmodel import specialize, enforceargs, always_inline
# from rpython.rlib import jit



class Bindings:
    MINSIZE = 8
    PERTURB_SHIFT = 5

    def __init__(self):
        from obin.objects.space import newundefined
        self._minsize = Bindings.MINSIZE
        self._perturb_shift = Bindings.PERTURB_SHIFT
        self._backing = None
        self._used = 0
        self._deleted = 0
        self.empty_pair = (newundefined(), absent_index())

        self._build(self._minsize)

    def _lookup(self, key):
        from obin.objects.space import isundefined
        backing = self._backing
        for i in self._indices(key, len(backing)):
            kv_pair = backing[i]
            _key = kv_pair[0]
            if isundefined(_key) or api.n_equal(_key, key):
                return i, kv_pair

        return absent_index(), self.empty_pair

    def get(self, key):
        # Performs a lookup to find the index and value of the key
        # in the backing structure
        i, kv_pair = self._lookup(key)
        if self.is_empty_pair(kv_pair):
            raise KeyError()

        return kv_pair[1]

    def is_empty_pair(self, kv_pair):
        if is_absent_index(kv_pair[1]):
            return True
        return False

    def insert(self, key, value):
        from obin.objects.space import isundefined, isany
        assert isany(key)
        assert not isundefined(key)
        assert isinstance(value, int)
        """
        Sets the value of the Hashmap at the key. It resizes the backing
        structure if the utilization of the Hashmap is > ~ 2/3
        """
        i, kv_pair = self._lookup(key)
        self._backing[i] = (key, value)
        if self.is_empty_pair(kv_pair):
            self._used += 1

        size = len(self._backing)
        utilization = (self._used * 1.0) / size
        if utilization > 0.67:
            self._resize(self._incr_size(size))

    def contains(self, key):
        """key in x => boolean
        Returns true if key is contained in the Hashmap.
        """
        i, kv_pair = self._lookup(key)
        return not self.is_empty_pair(kv_pair)

    def keys(self):
        from obin.objects.space import isundefined
        l = []
        for kv_pair in self._backing:
            if kv_pair and not isundefined(kv_pair[0]):
                l.append(kv_pair[0])
        return l

    def __iter__(self):
        from obin.objects.space import isundefined
        for kv_pair in self._backing:
            if kv_pair and not isundefined(kv_pair[0]):
                yield kv_pair[0]

    def items(self):
        from obin.objects.space import isundefined
        for kv_pair in self._backing:
            if kv_pair and not isundefined(kv_pair[0]):
                yield kv_pair[0], kv_pair[1]

    def copy(self):
        # TODO OPTMIZE
        b = Bindings()
        for kv_pair in self._backing:
            if not self.is_empty_pair(kv_pair):
                b.insert(kv_pair[0], kv_pair[1])
        return b

    def length(self):
        return self._used - self._deleted

    def delete(self, key):
        """
        Sets the key in the Hashmap to absent, releasing the original
        item. It resizes the backing structure if the utilization of
        the Hashmap is < ~ 1/6
        """
        i, kv_pair = self._lookup(key)
        if not self.is_empty_pair(kv_pair):
            self._backing[i] = self.empty_pair
            self._deleted += 1

            size = len(self._backing)
            utilization = (self._used - self._deleted) / size
            if utilization < 0.16:
                self._resize(self._decr_size(size))
        else:
            raise KeyError('no such item!')

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
        self._backing = [self.empty_pair] * size
        self._used = 0
        self._deleted = 0
        for kv_pair in init:
            if not self.is_empty_pair(kv_pair):
                self.insert(kv_pair[0], kv_pair[1])

    def _incr_size(self, size):
        return size * 2

    def _decr_size(self, size):
        return max(self._minsize, size // 2)


class TableIterator(W_Root):
    def __init__(self, source, length):
        assert isinstance(source, W_Map)
        assert isinstance(length, int)
        self.index = 0
        self.source = source
        self.source_length = length

    def _next_(self):
        from obin.objects.space import newundefined, isundefined
        while True:
            if self.index >= self.source_length:
                return newundefined()

            pair = self.source.slot_bindings[self.index]
            self.index += 1
            key = pair[0]
            if isundefined(key):
                continue

            return key

    def _tostring_(self):
        return "<TableIterator %d:%d>" % (self.index, self.source_length)

    def _tobool_(self):
        if self.index >= self.source_length:
            return False
        return True


class W_Map(W_Cell):
    """
        Dict which supports access by key and by index
    """

    def __init__(self):
        W_Cell.__init__(self)

        self.slot_values = None
        self.slot_bindings = None
        self.index = 0

    def to_dict(self):
        m = {}
        for k, i in self.slot_bindings.items():
            m[k] = api.at_index(self.slot_values, i)

        return m

    def _tostring_(self):
        return str(self.to_dict())

    def __str__(self):
        return str(self.to_dict())

    def __repr__(self):
        return self.__str__()

    def _clone_(self):
        clone = W_Map()
        values = self.slot_values
        if values is not None:
            clone.slot_values = api.clone(self.slot_values)
            clone.slot_bindings = self.slot_bindings.copy()
            clone.index = self.index

        return clone

    def _iterator_(self):
        return TableIterator(self, self._length_())

    def _behavior_(self, process):
        return process.std.behaviors.Map

    def _at_(self, name):
        from obin.objects.space import newundefined
        idx = self._get_index_(name)
        if is_absent_index(idx):
            return newundefined()

        return self._at_index_(idx)

    def _get_index_(self, name):
        # from obin.objects import api
        # print "get_index", api.to_native_string(name)
        try:
            idx = self.slot_bindings.get(name)
            return idx
        except Exception as e:
            # print "get_index Exception", e
            # for k in self.property_bindings:
            #     print api.to_native_string(k),
            return absent_index()

    def _put_at_index_(self, idx, value):
        # accessing protected method instead of api.put_at_index for avoiding multiple 0 < idx < length check
        self.slot_values._put_at_index_(idx, value)

    def _at_index_(self, idx):
        # accessing protected method instead of api.at_index for avoiding multiple 0 < idx < length check
        return self.slot_values._at_index_(idx)

    def _put_(self, name, value):
        self.insert(name, value)

    def insert(self, name, value):
        from obin.objects.space import isany
        assert isany(name)
        assert isany(value)
        # print "Slots_ass", api.to_native_string(name), api.to_native_string(value)
        idx = self._get_index_(name)
        # print "Slots_add, IDX", idx
        if is_absent_index(idx):
            idx = self.index
            self.slot_bindings.insert(name, idx)
            self.index += 1

        # print "Slots_add, IDX >>", idx
        self.slot_values.ensure_size(idx + 1)
        self._put_at_index_(idx, value)
        return idx

    def contains(self, name):
        return name in self.slot_bindings

    def _length_(self):
        return self.slot_values._length_()

    def keys(self):
        return self.slot_bindings.keys()

    def _remove_at_(self, name):
        idx = self._get_index_(name)
        if is_absent_index(idx):
            raise RuntimeError("Illegal call")

        assert idx >= 0
        self.slot_values.exclude_index(idx)
        del self.slot_bindings[name]


def _create_map(values, bindings, index):
    map = W_Map()
    map.slot_bindings = bindings
    map.slot_values = values
    map.index = index
    return map


def create_map_with_size(size):
    from obin.objects.space import newvector
    return _create_map(newvector([None] * size), Bindings(), 0)


def create_empty_map():
    from obin.objects.space import newvector
    return _create_map(newvector([]), Bindings(), 0)


def create_map_with_values_from_map(values, source):
    l = api.n_length(source)
    size = api.n_length(values)
    diff = l - size
    assert diff >= 0
    if diff > 0:
        values.append_value_multiple_times(None, diff)

    bindings = source.slot_bindings.copy()
    return _create_map(values, bindings, source.index)
