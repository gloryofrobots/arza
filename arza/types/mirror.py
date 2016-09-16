from arza.types import root, api, space, plist, datatype
from arza.runtime import error


class W_MirrorType(datatype.W_BaseDatatype):
    def __init__(self, name, interfaces):
        datatype.W_BaseDatatype.__init__(self, name, interfaces)

    def _type_(self, process):
        return process.std.types.Datatype


class W_Mirror(root.W_Root):
    def __init__(self, source, interfaces):
        self.source = source
        type_name = space.newstring(u"<MirrorType %s>" % api.to_s(interfaces))
        self.type = W_MirrorType(type_name, interfaces)

    def _to_repr_(self):
        return self._to_string_()

    def _at_(self, key):
        return self.source._at_(key)

    def _contains_(self, key):
        return self.source._contains_(key)

    def _at_index_(self, i):
        return self.source._at_index_(i)

    def _get_index_(self, obj):
        return self.source._get_index_(obj)

    def _put_at_index_(self, i, obj):
        return self.source._put_at_index_(i, obj)

    def _is_empty_(self):
        return self.source._is_empty_()

    def _length_(self):
        return self.source._length_()

    def _put_(self, k, v):
        return self.source._put_(k, v)

    def _remove_at_(self, key):
        return self.source._remove_at_(key)

    def _to_string_(self):
        return self.source._to_string_()

    def _to_bool_(self):
        return self.source._to_bool_()

    def _to_integer_(self):
        return self.source._to_integer_()

    def _to_float_(self):
        return self.source._to_float_()

    def _equal_(self, other):
        return self.source._equal_()

    def _hash_(self):
        return self.source._hash_()

    def _compare_(self, other):
        return self.source._compare_(other)

    def _call_(self, process, args):
        return self.source._call_(process, args)

    def _type_(self, process):
        return self.type

    def _compute_hash_(self):
        return self.source._compute_hash_()

    def _to_routine_(self, stack, args):
        return self.source._to_routine_(stack, args)

    def _clone_(self):
        return self.source._clone_()


def mirror(source, interfaces):
    error.affirm_type(interfaces, space.islist)
    error.affirm_iterable(interfaces, space.isinterface)

    if space.ismirror(source):
        source = source.source

    error.affirm_type(source, space.isrecord)

    return W_Mirror(source, interfaces)
