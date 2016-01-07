from obin.objects.types.root import W_Cell
from obin.runtime.error import ObinTraitError
from obin.objects import api

def _tostring_foldl_(traits, trait):
    traits.append(api.tostring(trait.name))
    return traits

class W_Entity(W_Cell):
    # _immutable_fields_ = ['_slots']

    def __init__(self, behavior, source):
        W_Cell.__init__(self)
        self.source = source
        self.behavior = behavior

    def _tostring_(self):
        from obin.objects import api
        from obin.objects.space import newvector
        from obin.objects.types.plist import foldl
        traits_repr = foldl(_tostring_foldl_, newvector([]), self.behavior.traits)
        traits_repr = ",".join([api.to_native_string(t) for t in traits_repr.to_n_list()])

        return "<entity of %s and %s>" % (api.to_native_string(self.source), traits_repr)

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
        self.source._put_(k, v)

    def _remove_at_(self, key):
        self.source._remove_at_(key)

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

    def _behavior_(self, process):
        return self.behavior

    def _compute_hash_(self):
        return self.source._compute_hash_()

    def _to_routine_(self, stack, args):
        return self.source._to_routine_(stack, args)

    def _clone_(self):
        source = api.clone(self.source)
        return W_Entity(self.behavior, source)


def has_traits(entity):
    return entity.traits is not None


def attach(process, entity, trait):
    from obin.objects.space import isentity, istrait, newbehavior, newentity
    assert istrait(trait)
    assert isentity(entity)
    traits = entity.behavior.traits
    from obin.objects.types.plist import prepend
    return newentity(process, newbehavior(prepend(traits, trait)), entity.source)


def detach(process, entity, trait):
    from obin.objects.space import isentity, istrait, newbehavior, newentity
    from obin.objects.types.plist import remove
    assert istrait(trait)
    assert isentity(entity)
    traits = entity.behavior.traits
    try:
        return newentity(process, newbehavior(remove(traits, trait)), entity.source)
    except:
        raise ObinTraitError(u"Detach trait error", trait)
