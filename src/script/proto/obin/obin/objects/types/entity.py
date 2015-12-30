from obin.objects.types.root import W_Cell
from obin.runtime.error import ObinTraitError
from obin.objects import api


class W_Entity(W_Cell):
    # _immutable_fields_ = ['_slots']

    def __init__(self, traits, source):
        W_Cell.__init__(self)
        self.source = source
        self.traits = traits

    def __str__(self):
        return "<Entity of %s >" % (str(self.source))

    def __repr__(self):
        return self.__str__()

    # BEHAVIOR
    def _at_(self, key):
        return self.source._at_(key)

    def _at_index_(self, i):
        return self.source._at_index_(i)

    def _get_index_(self, key):
        return self.source._get_index_(key)

    def _put_at_index_(self, i, val):
        self.source._put_at_index_(i, val)

    def _length_(self):
        return self.source._length_()

    def _put_(self, k, v):
        self.source._put_at_index_(k, v)

    def _remove_at_(self, key):
        self.source._remove_at_(key)

    def _tostring_(self):
        return self.source._tostring_()

    def _tobool_(self):
        return self.source._tobool_()

    def _tointeger_(self):
        return self.source._tointeger_()

    def _tofloat_(self):
        return self.source._tofloat_()

    def _equal_(self, other):
        return self.source._equal_(other)

    def _hash_(self):
        return self.source._hash_()

    def _compare_(self, other):
        return self.source._compare_(other)

    def _call_(self, process, args):
        return self.source._call_(process, args)

    def _slice_(self, start, end, step):
        return self.source._slice_(start, end, step)

    def _kindof_(self, trait):
        if self.traits.has(trait):
            return True

        return False

    def _traits_(self, process):
        return self.traits

    def _totrait_(self, process):
        return self.source._totrait_(process)

    def _compute_hash_(self):
        return self.source._compute_hash_()

    def _to_routine_(self, args):
        return self.source._to_routine_()

    def _clone_(self):
        source = api.clone(self.source)
        traits = self.traits.copy()
        return W_Entity(traits, source)


def has_traits(entity):
    return entity.traits is not None


def attach(process, entity, trait):
    from obin.objects.space import isentity, istrait
    assert istrait(trait)
    assert isentity(entity)
    entity.traits.prepend(trait)


def detach(process, entity, trait):
    from obin.objects.space import isentity, istrait
    assert isentity(entity)
    assert istrait(trait)
    try:
        entity.traits.remove(trait)
    except KeyError:
        raise ObinTraitError(u"Detach trait error", trait)


def set_traits(entity, traits):
    from obin.objects.space import isentity
    assert isentity(entity)
    assert entity.traits is None
    entity.traits = traits
