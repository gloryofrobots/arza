from obin.objects.object_space import _w
from obin.runtime.routine import complete_native_routine
from obin.runtime.exception import ObinTypeError
from obin.builtins import get_arg


@complete_native_routine
def to_string(ctx, routine):
    this, args = routine.args()
    from obin.objects.object_space import isfunction
    assert isfunction(this)
    return this._to_string_()


@complete_native_routine
def empty(ctx, routine):
    from obin.objects.object_space import newundefined
    return newundefined()


# 15.3.4.4 Function.prototype.call
def js_call(ctx, routine):
    from obin.objects.object_space import isfunction
    func = ctx.this_binding()
    args = ctx.argv()

    assert isfunction(func)

    this_arg = get_arg(args, 0)
    arg_list = args[1:]

    routine2 = func.create_routine(args=arg_list, this=this_arg, calling_context=ctx)
    routine.call_routine(routine2)


# 15.3.4.3 Function.prototype.apply (thisArg, argArray)
def js_apply(ctx, routine):
    from obin.runtime.machine import run_routine_for_result
    from obin.objects.object_space import isnull_or_undefined
    func = ctx.this_binding()
    args = ctx.argv()

    this_arg = get_arg(args, 0)
    arg_array = get_arg(args, 1)
    if isnull_or_undefined(arg_array):
        routine = func.create_routine(args=[], this=this_arg, calling_context=ctx)
        result = run_routine_for_result(routine)
        return _w(result)

    from obin.objects.object import W_Array

    if not isinstance(arg_array, W_Array):
        raise ObinTypeError(u'W__Array expected')

    n = arg_array.length()
    arg_list = []
    index = 0
    while index < n:
        index_name = unicode(str(index))
        next_arg = arg_array.get(index_name)
        arg_list.append(next_arg)
        index += 1

    routine2 = func.create_routine(args=arg_list, this=this_arg, calling_context=ctx)
    routine.call_routine(routine2)
    # result = run_routine_for_result(routine2)
    # routine.complete(_w(result))
