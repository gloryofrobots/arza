from obin.runtime.exception import JsTypeError
from obin.builtins import get_arg
from obin.objects.object_space import w_return, _w


@w_return
def to_string(this, args):
    from obin.objects.object import W_BasicFunction
    if not isinstance(this, W_BasicFunction):
        raise JsTypeError(u'')

    return this._to_string_()


@w_return
def empty(this, args):
    from obin.objects.object_space import newundefined
    return newundefined()


# 15.3.4.4 Function.prototype.call
def js_call(ctx):
    func = ctx.this_binding()
    args = ctx.argv()

    if not func.is_callable():
        raise JsTypeError(u'')

    this_arg = get_arg(args, 0)
    arg_list = args[1:]

    routine = func.create_routine(args=arg_list, this=this_arg, calling_context=ctx)
    from obin.runtime.machine import run_routine_for_result
    result = run_routine_for_result(routine)
    return result


# 15.3.4.3 Function.prototype.apply (thisArg, argArray)
def js_apply(ctx):
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

    from obin.objects.object import W__Array

    if not isinstance(arg_array, W__Array):
        raise JsTypeError(u'W__Array expected')

    n = arg_array.length()
    arg_list = []
    index = 0
    while index < n:
        index_name = unicode(str(index))
        next_arg = arg_array.get(index_name)
        arg_list.append(next_arg)
        index += 1

    routine = func.create_routine(args=arg_list, this=this_arg, calling_context=ctx)
    result = run_routine_for_result(routine)
    return _w(result)
