from obin.objects.object_space import _w
from obin.runtime.routine import complete_native_routine
from obin.builtins import get_arg
from obin.objects import api

def setup(obj):
    api.put_native_function(obj, u'toString', to_string)
    api.put_native_function(obj, u'clone', clone)
    api.put_native_function(obj, u'at', at)
    api.put_native_function(obj, u'create', create)
    pass

@complete_native_routine
def at(ctx, routine):
    this, args = routine.args()
    key = get_arg(args, 0)
    return api.at(this, key)

@complete_native_routine
def clone(ctx, routine):
    this, args = routine.args()
    return api.clone(this)

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