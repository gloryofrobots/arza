from obin.objects.object_space import _w
from obin.builtins import get_arg

def clone(this, args):
    import copy
    clone = copy.copy(this)
    clone._slots = copy.deepcopy(this._slots)
    return clone

def create(this, args):
    from obin.objects.object_space import object_space
    obj = object_space.new_obj()
    object_space.assign_proto(obj, this)
    return obj

def to_string(this, args):
    s = "[%s<%s> %s]" % (this.klass(), str(hex(id(this))), str(this.named_properties()))
    return _w(s)


def value_of(this, args):
    return this

def has_own_property(this, args):
    arg = get_arg(args, 0)
    s = arg.to_string()
    result = this.has_property(s)
    return _w(result)