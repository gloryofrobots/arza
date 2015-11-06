from obin.objects.object_space import _w
from obin.runtime.routine import complete_native_routine
from obin.builtins import get_arg
from obin.objects import api

def setup(obj):
    api.put_native_function(obj, u'toString', to_string)
    api.put_native_function(obj, u'clone', clone)
    api.put_native_function(obj, u'at', at)
    api.put_native_function(obj, u'lookup', lookup)
    api.put_native_function(obj, u'isa', isa)
    api.put_native_function(obj, u'nota', nota)
    api.put_native_function(obj, u'kindof', kindof)
    api.put_native_function(obj, u'create', create)
    api.put_native_function(obj, u'traits', traits)
    pass

def object_extract_1_obj_arg(routine):
    from obin.objects.object_space import isobject
    this, args = routine.method_args()
    other = get_arg(args, 0)
    assert isobject(this)
    assert isobject(other)
    return this, other

@complete_native_routine
def traits(ctx, routine):
    from obin.objects.object_space import isobject
    this, args = routine.method_args()
    assert isobject(this)
    return this.traits()

@complete_native_routine
def isa(ctx, routine):
    this, other = object_extract_1_obj_arg(routine)
    return this.isa(other)

@complete_native_routine
def nota(ctx, routine):
    this, other = object_extract_1_obj_arg(routine)
    return this.nota(other)

@complete_native_routine
def kindof(ctx, routine):
    this, other = object_extract_1_obj_arg(routine)
    return this.kindof(other)

@complete_native_routine
def at(ctx, routine):
    this, args = routine.method_args()
    key = get_arg(args, 0)
    return api.at(this, key)

@complete_native_routine
def lookup(ctx, routine):
    this, args = routine.method_args()
    key = get_arg(args, 0)
    return api.lookup(this, key)

@complete_native_routine
def clone(ctx, routine):
    this, args = routine.method_args()
    return api.clone(this)

@complete_native_routine
def create(ctx, routine):
    from obin.objects.object_space import object_space
    this, args = routine.method_args()
    obj = object_space.newobject()
    obj.isa(this)
    return obj

@complete_native_routine
def to_string(ctx, routine):
    this, args = routine.method_args()
    s = "[%s<%s> %s]" % (this.klass(), str(hex(id(this))), str(this.named_properties()))
    return _w(s)


@complete_native_routine
def value_of(ctx, routine):
    this, args = routine.method_args()
    return this

@complete_native_routine
def has_own_property(ctx, routine):
    this, args = routine.method_args()
    arg = get_arg(args, 0)
    s = arg.to_string()
    result = this.has_property(s)
    return _w(result)