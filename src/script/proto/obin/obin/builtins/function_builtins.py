from obin.objects import api
from obin.runtime.routine import complete_native_routine

def setup(obj):
    api.put_native_function(obj, u'arity', arity, 1)
    api.put_native_function(obj, u'isVariadic', is_variadic, 1)
    obj.freeze()

@complete_native_routine
def arity(routine):
    from obin.objects.object_space import isfunction, newint
    this = routine.get_arg(0)
    assert isfunction(this)
    return newint(this.arity())

@complete_native_routine
def is_variadic(routine):
    from obin.objects.object_space import isfunction, newbool
    this = routine.get_arg(0)
    assert isfunction(this)
    return newbool(this.is_variadic())
