from obin.objects import api
from obin.runtime.routine import complete_native_routine

def setup(obj):
    api.put_native_function(obj, u'arity', arity)
    api.put_native_function(obj, u'isVariadic', is_variadic)
    obj.freeze()

@complete_native_routine
def arity(ctx, routine):
    from obin.objects.object_space import isfunction, newint
    this = routine.args()[0]
    assert isfunction(this)
    return newint(this.arity())

@complete_native_routine
def is_variadic(ctx, routine):
    from obin.objects.object_space import isfunction, newbool
    this = routine.args()[0]
    assert isfunction(this)
    return newbool(this.is_variadic())
