from obin.runtime.routine import complete_native_routine
from obin.objects import api

def setup(obj):
    api.put_primitive_function(obj, u'clone', clone, 1)
    api.put_primitive_function(obj, u'at', at, 2)
    api.put_primitive_function(obj, u'lookup', lookup, 2)
    api.put_primitive_function(obj, u'isa', isa, 2)
    api.put_primitive_function(obj, u'nota', nota, 2)
    api.put_primitive_function(obj, u'kindof', kindof, 2)
    api.put_primitive_function(obj, u'create', create, 1)
    api.put_primitive_function(obj, u'traits', traits, 1)

    api.put_string_string(obj, u'__name__', u"Object")

    obj.freeze()

def object_extract_1_obj_arg(routine):
    from obin.objects.space import isobject
    this = routine.get_arg(0)
    other = routine.get_arg(1)
    assert isobject(this)
    assert isobject(other)
    return this, other

@complete_native_routine
def traits(routine):
    from obin.objects.space import isobject
    this = routine.get_arg(0)
    assert isobject(this)
    return this.traits()

@complete_native_routine
def isa(routine):
    this, other = object_extract_1_obj_arg(routine)
    raise NotImplementedError()

@complete_native_routine
def nota(routine):
    this, other = object_extract_1_obj_arg(routine)
    raise NotImplementedError()

@complete_native_routine
def kindof(routine):
    this, other = object_extract_1_obj_arg(routine)
    raise NotImplementedError()

@complete_native_routine
def at(routine):
    this = routine.get_arg(0)
    key = routine.get_arg(1)
    return api.at(this, key)

@complete_native_routine
def lookup(routine):
    this = routine.get_arg(0)
    key = routine.get_arg(1)
    return api.lookup(this, key)

@complete_native_routine
def clone(routine):
    this = routine.get_arg(0)
    return api.clone(this)

@complete_native_routine
def create(routine):
    from obin.objects.space import state
    this = routine.get_arg(0)
    obj = state.newobject()
    obj.set_origin(this)
    return obj

