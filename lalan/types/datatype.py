from lalan.types.root import W_Hashable
from lalan.types import api, space, plist
from lalan.misc import platform
from lalan.runtime import error


class W_Instance(W_Hashable):
    def __init__(self, type, values):
        W_Hashable.__init__(self)
        self.values = values
        self.type = type

    def _to_string_(self):
        res = []

        for f in self.type.fields:
            i = api.at(self.type.descriptors, f)
            v = api.at_index(self.values, api.to_i(i))
            res.append("%s = %s" % (api.to_s(f), api.to_s(v)))

        return "<%s (%s)>" % (api.to_s(self.type), ", ".join(res))

    def _to_repr_(self):
        res = []

        for f in self.type.fields:
            i = api.at(self.type.descriptors, f)
            v = api.at_index(self.values, api.to_i(i))
            res.append("%s = %s" % (api.to_r(f), api.to_r(v)))

        return "<%s (%s)>" % (api.to_r(self.type), ", ".join(res))

    def _type_(self, process):
        return self.type

    def _at_(self, name):
        if space.isint(name):
            return self._at_index_(api.to_i(name))

        idx = api.lookup(self.type.descriptors, name, space.newvoid())
        if space.isvoid(idx):
            error.throw_1(error.Errors.KEY_ERROR, name)
        return api.at(self.values, idx)

    def _contains_(self, key):
        value = self._at_(key)
        return not space.isvoid(value)

    def _at_index_(self, idx):
        # accessing protected method instead of api.at_index for avoiding multiple 0 < idx < length check
        return self.values._at_index_(idx)

    def _put_(self, name, value):
        idx = api.lookup(self.type.descriptors, name, space.newvoid())
        if space.isvoid(idx):
            error.throw_1(error.Errors.KEY_ERROR, name)

        newvalues = api.put(self.values, name, value)
        return W_Instance(self.type.descriptors, newvalues)

    def _length_(self):
        return api.length(self.values)

    def _equal_(self, other):
        if not isinstance(other, W_Instance):
            return False
        if not api.equal_b(self.type, other.type):
            return False
        return api.equal_b(self.values, other.values)

    def keys(self):
        return self.type.fields

    def values(self):
        return self.values

    def index_of(self, val):
        idx = self.values.index(val)
        if platform.is_absent_index(idx):
            error.throw_1(error.Errors.VALUE_ERROR, val)
        return idx


def descriptors(fields):
    d = space.newmap()
    for i in range(len(fields)):
        f = fields[i]
        d = api.put(d, f, space.newint(i))
    return d


class MRO:
    def __init__(self):
        self.items = plist.empty()
        self.interfaces_index = 0

    def add_interface(self, interface):
        self.items = plist.insert(self.items, self.interfaces_index, interface)

    def add_type(self, type):
        self.items = plist.cons(type, self.items)
        self.interfaces_index += 1

    def weight(self, item):
        return plist.index(self.items, item)

    def has_type(self, type):
        return plist.contains(plist.take(self.items, self.interfaces_index), type)

    def has_interface(self, type):
        return plist.contains(plist.drop(self.items, self.interfaces_index), type)


class W_DataType(W_Hashable):
    def __init__(self, name, fields):
        W_Hashable.__init__(self)

        self.interfaces = plist.empty()
        self.mro = MRO()
        self.generics = space.newmap()

        self.name = name
        self.fields = fields
        self.arity = api.length_i(self.fields)

        if plist.is_empty(self.fields):
            self.is_singleton = True
        else:
            self.is_singleton = False

        self.descriptors = descriptors(self.fields)

    def register_interface(self, iface):
        if self.is_interface_implemented(iface):
            error.throw_3(error.Errors.IMPLEMENTATION_ERROR, space.newstring(u"Interface has already implemented"),
                          self, iface)

        self.interfaces = plist.cons(iface, self.interfaces)
        self.mro.add_interface(iface)

        # register all currently implemented generics for this interface
        for t in iface.registered_generics:
            generic = api.at_index(t, 0)
            position = api.at_index(t, 1)
            self.register_generic(generic, position)

        iface.register_type(self)

    def is_interface_implemented(self, iface):
        return plist.contains(self.interfaces, iface)

    def _can_implement(self, iface):
        if plist.is_empty(iface.generics):
            return False

        for record in iface.generics:
            generic = api.at_index(record, 0)
            position = api.at_index(record, 1)
            if not self.is_generic_implemented(generic, position):
                return False

        return True

    def register_generic(self, generic, position):
        if not api.contains_b(self.generics, generic):
            api.put(self.generics, generic, space.newlist([]))

        l = api.at(self.generics, generic)

        if api.contains_b(l, position):
            return

        api.put(
            self.generics,
            generic,
            plist.cons(position, l)
        )

        # Check if any of interfaces is completed by the moment
        for record in generic.interfaces:
            interface = api.at_index(record, 0)
            if self.is_interface_implemented(interface):
                continue
            if self._can_implement(interface):
                self.register_interface(interface)

    def is_generic_implemented(self, generic, position):
        if not api.contains_b(self.generics, generic):
            return False
        positions = api.at(self.generics, generic)
        return plist.contains(positions, position)

    def _call_(self, process, args):
        length = api.length_i(args)
        if length != self.arity:
            error.throw_4(error.Errors.CONSTRUCTOR_ERROR,
                          space.newstring(u"Invalid count of data for construction of type"),
                          self,
                          api.length(self.fields),
                          args)

        return W_Instance(self, space.newpvector(args.to_l()))

    def _type_(self, process):
        return process.std.types.Datatype

    def _compute_hash_(self):
        return int((1 - platform.random()) * 10000000)

    def _to_string_(self):
        return api.to_s(self.name)
        # return "<trait %s>" % (api.to_s(self.name))

    def _to_repr_(self):
        return self._to_string_()

    def _equal_(self, other):
        return other is self


def record_index_of(record, obj):
    error.affirm_type(record, space.isrecord)
    return record.index_of(obj)


def record_keys(record):
    error.affirm_type(record, space.isrecord)
    return record.keys()


def record_values(record):
    error.affirm_type(record, space.isrecord)
    return record.values()


def newtype(process, name, fields):
    _type = W_DataType(name, fields)
    _type.register_interface(process.std.interfaces.Any)
    if _type.is_singleton:
        _type.register_interface(process.std.interfaces.Singleton)
    else:
        _type.register_interface(process.std.interfaces.Instance)
    return _type
