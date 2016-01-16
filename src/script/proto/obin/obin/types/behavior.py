from obin.types.root import W_Hashable
from obin.types import api


class W_Behavior(W_Hashable):
    # _immutable_fields_ = ['_slots']

    def __init__(self, traits):
        W_Hashable.__init__(self)
        from obin.types.space import islist
        assert islist(traits)
        self.traits = traits

    def _tostring_(self):
        return "<Behavior %s>" % (api.to_native_string(self.traits))

    def _behavior_(self, process):
        return process.std.behaviors.Behavior

    def _clone_(self):
        return W_Behavior(self.traits)

    def _compute_hash_(self):
        from obin.types.plist import compute_hash
        return compute_hash(self.traits)


def traits(process, obj):
    b = api.behavior(process, obj)
    return b.traits
