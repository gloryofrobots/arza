from obin.objects.object_space import _w
from obin.runtime.routine import complete_native_routine
from obin.builtins import get_arg

@complete_native_routine
def clone(ctx, routine):
    import copy
    this, args = routine.args()
    clone = copy.copy(this)
    clone._slots = copy.deepcopy(this._slots)
    return clone

@complete_native_routine
def create(ctx, routine):
    from obin.objects.object_space import object_space
    this, args = routine.args()
    obj = object_space.newobject()
    object_space.assign_proto(obj, this)
    return obj

@complete_native_routine
def to_string(ctx, routine):
    this, args = routine.args()
    s = "[%s<%s> %s]" % (this.klass(), str(hex(id(this))), str(this.named_properties()))
    return _w(s)


@complete_native_routine
def value_of(ctx, routine):
    this, args = routine.args()
    return this

@complete_native_routine
def has_own_property(ctx, routine):
    this, args = routine.args()
    arg = get_arg(args, 0)
    s = arg.to_string()
    result = this.has_property(s)
    return _w(result)