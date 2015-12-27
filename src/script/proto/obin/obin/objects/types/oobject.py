from obin.objects.types.oroot import W_Cell
from obin.objects.types.ovalue import W_ValueType
from obin.runtime.error import ObinTraitError
from obin.objects import api
from obin.objects.otable import newtable_empty


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
            slots = newtable_empty()
        self.slots = slots
        self.traits = None
        self.trait = None

    def _at_(self, k):
        v = self.slots._at_(k)
        return v

    def _at_index_(self, i):
        return self.slots._at_index_(i)

    def _get_index_(self, obj):
        return self.slots._get_index_(obj)

    def _put_at_index_(self, i, obj):
        self.slots._put_at_index_(i, obj)

    def _put_(self, k, v):
        self.slots._put_(k, v)

    def _iterator_(self):
        keys = self.slots.keys()
        return ObjectIterator(keys, len(keys))

    def _tobool_(self):
        return True

    def _length_(self):
        return self.slots._length_()

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

    def _traits_(self, process):
        if self.traits is None:
            return process.stdlib.traits.ObjectTraits

        return self.traits

    def _totrait_(self, process):
        if not self.trait:
            _create_trait(process, self)
        return self.trait


def has_traits(obj):
    return obj.traits is not None


def _create_trait(process, obj):
    from obin.objects.space import newtrait, newstring
    assert obj.traits
    assert not obj.trait
    obj.trait = newtrait(newstring(u""))
    attach(process, obj, obj.trait)


def attach(process, obj, trait):
    from obin.objects.space import isobject, istrait
    assert istrait(trait)
    assert isobject(obj)
    if obj.traits is None:
        obj.traits = api.clone(process.stdlib.traits.ObjectTraits)
    obj.traits.prepend(trait)


def detach(process, obj, trait):
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
