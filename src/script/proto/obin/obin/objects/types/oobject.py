from obin.objects.types.oroot import W_Cell
from obin.objects.types.ovalue import W_ValueType
from obin.runtime.exception import ObinTraitError
from obin.objects import api
from obin.objects.slots import newslots_empty


class ObjectIterator(W_ValueType):
    def __init__(self, source, length):
        assert isinstance(source, list)
        assert isinstance(length, int)
        self.index = 0
        self.source = source
        self.__source_length = length

    def _next_(self):
        from obin.objects.space import newundefined
        if self.index >= self.__source_length:
            return newundefined()

        el = self.source[self.index]
        self.index += 1
        return el

    def _tostring_(self):
        return "<Iterator %d:%d>" % (self.index, self.__source_length)

    def _tobool_(self):
        if self.index >= self.__source_length:
            return False
        return True


class W_Object(W_Cell):
    # _immutable_fields_ = ['_slots']

    def __init__(self, slots):
        W_Cell.__init__(self)
        if slots is None:
            slots = newslots_empty()
        self.slots = slots
        self.traits = None
        self.trait = None

    def _at_(self, k):
        v = self.slots.get(k)
        return v

    def _lookup_(self, k):
        return self._at_(k)

    def _put_(self, k, v):
        self.slots.add(k, v)

    def _iterator_(self):
        keys = self.slots.keys()
        return ObjectIterator(keys, len(keys))

    def _tobool_(self):
        return True

    def _length_(self):
        return self.slots.length()

    def _tostring_(self):
        return str("{%s %s}" % (str(self.slots), str(self.traits)))

    def _clone_(self):
        slots = self.slots.copy()
        clone = W_Object(slots)
        traits = self.traits.copy()
        set_traits(clone, traits)
        return clone

    def _kindof_(self, trait):
        if self.traits.has(trait):
            return True

        return False

    def _traits_(self):
        return self.traits

    def _totrait_(self):
        if not self.trait:
            _create_trait(self)
        return self.trait


def has_traits(obj):
    return obj.traits is not None


def _create_trait(obj):
    from obin.objects.space import newtrait, newstring
    assert obj.traits
    assert not obj.trait
    obj.trait = newtrait(newstring(u""))
    attach(obj, obj.trait)


def put_by_index(obj, idx, value):
    obj.slots.set_by_index(idx, value)


def get_by_index(obj, idx):
    return obj.slots.get_by_index(idx)


def get_index(obj, name):
    return obj.slots.get_index(name)


def traits(obj):
    if obj.traits is None:
        from obin.objects.space import state
        return state.traits.ObjectTraits

    return obj.traits


def attach(obj, trait):
    from obin.objects.space import isobject, istrait, state
    assert istrait(trait)
    assert isobject(obj)
    if obj.traits is None:
        obj.traits = api.clone(state.traits.ObjectTraits)
    obj.traits.prepend(trait)


def detach(obj, trait):
    from obin.objects.space import isobject, istrait
    assert isobject(obj)
    assert istrait(trait)
    try:
        obj.traits.remove(trait)
    except KeyError:
        raise ObinTraitError(u"Detach trait error", trait)


def set_traits(obj, traits):
    from obin.objects.space import isobject
    assert isobject(obj)
    assert obj.traits is None
    obj.traits = traits
