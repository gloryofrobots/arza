from obin.objects.space import newvector
from obin.objects.space import newundefined, isundefined, isany
from obin.objects import api
from obin.utils.builtins import is_absent_index, absent_index
from rpython.rlib.objectmodel import specialize, enforceargs, always_inline
from rpython.rlib import jit



class Bindings:
    MINSIZE = 8
    PERTURB_SHIFT = 5

    def __init__(self):
        self._minsize = Bindings.MINSIZE
        self._perturb_shift = Bindings.PERTURB_SHIFT
        self._backing = None
        self._used = 0
        self._deleted = 0
        self.empty_pair = (newundefined(), absent_index())

        self._build(self._minsize)

    def _lookup(self, key):
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

    def set(self, key, value):
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
        l = []
        for kv_pair in self._backing:
            if kv_pair and not isundefined(kv_pair[0]):
                l.append(kv_pair[0])
        return l

    def __iter__(self):
        for kv_pair in self._backing:
            if kv_pair and not isundefined(kv_pair[0]):
                yield kv_pair[0]

    def items(self):
        for kv_pair in self._backing:
            if kv_pair and not isundefined(kv_pair[0]):
                yield kv_pair[0], kv_pair[1]

    def copy(self):
        # TODO OPTMIZE
        b = Bindings()
        for kv_pair in self._backing:
            if not self.is_empty_pair(kv_pair):
                b.set(kv_pair[0], kv_pair[1])
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
                self.set(kv_pair[0], kv_pair[1])

    def _incr_size(self, size):
        return size * 2

    def _decr_size(self, size):
        return max(self._minsize, size // 2)



class Slots:
    """
        Dict which supports access by key and by index
    """

    def __init__(self):
        self.slot_values = None
        self.slot_bindings = None
        self.index = 0

    def to_dict(self):
        m = {}
        for k, i in self.slot_bindings.items():
            m[k] = self.slot_values.at(i)

        return m

    def __str__(self):
        return str(self.to_dict())
        pass

    def __repr__(self):
        return self.__str__()

    def copy(self):
        clone = Slots()
        values = self.slot_values
        if values is not None:
            clone.slot_values = self.slot_values.copy()
            clone.slot_bindings = self.slot_bindings.copy()
            clone.index = self.index

        return clone

    def contains(self, name):
        return name in self.slot_bindings

    def length(self):
        return self.slot_values.length()

    def keys(self):
        return self.slot_bindings.keys()

    def get(self, name):
        from obin.objects.space import newundefined
        idx = self.get_index(name)
        if is_absent_index(idx):
            return newundefined()

        return self.get_by_index(idx)

    def get_index(self, name):
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

    def set_by_index(self, idx, value):
        self.slot_values.set(idx, value)

    def get_by_index(self, idx):
        # print "Slots.get_by_index", idx
        return self.slot_values.at(idx)

    def set(self, name, value):
        from obin.objects.space import isany
        assert isany(name)
        assert isany(value)
        idx = self.get_index(name)
        self.set_by_index(idx, value)

    def add(self, name, value):
        from obin.objects.space import isany
        assert isany(name)
        assert isany(value)
        # print "Slots_ass", api.to_native_string(name), api.to_native_string(value)
        idx = self.get_index(name)
        # print "Slots_add, IDX", idx
        if is_absent_index(idx):
            idx = self.index
            self.slot_bindings.set(name, idx)
            self.index += 1

        # print "Slots_add, IDX >>", idx
        self.slot_values.ensure_size(idx + 1)
        # if idx >= self.property_values.length():
        #     values = self.property_values.values()
        #     values = values + ([None] * (1 + idx - len(values)))
        #     self.property_values.set_values(values)

        self.set_by_index(idx, value)
        return idx

    def delete(self, name):
        idx = self.get_index(name)
        if is_absent_index(idx):
            return

        assert idx >= 0
        self.slot_values.exclude_index(idx)
        del self.slot_bindings[name]


def newslots(values, bindings, index):
    slots = Slots()
    slots.slot_bindings = bindings
    slots.slot_values = values
    slots.index = index
    return slots


def newslots_with_size(size):
    return newslots(newvector([None] * size), Bindings(), 0)


def newslots_empty():
    return newslots(newvector([]), Bindings(), 0)


def newslots_with_values_from_slots(values, protoslots):
    l = protoslots.length()
    size = values.length()
    diff = l - size
    assert diff >= 0
    if diff > 0:
        values.append_value_multiple_times(None, diff)

    bindings = protoslots.slot_bindings.copy()
    index = protoslots.index
    return newslots(values, bindings, index)
