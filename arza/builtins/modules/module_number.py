from arza.types import number, space, api
from arza.runtime.routine.routine import complete_native_routine
from arza.runtime import error


def setup(process, stdlib):
    _module_name = space.newsymbol(process, u'arza:lang:_number')
    _module = space.newemptyenv(_module_name)
    api.put_native_function(process, _module, u'pow', _pow, 2)
    api.put_native_function(process, _module, u'add', add, 2)
    api.put_native_function(process, _module, u'sub', sub, 2)
    api.put_native_function(process, _module, u'mul', mul, 2)
    api.put_native_function(process, _module, u'div', div, 2)
    api.put_native_function(process, _module, u'mod', mod, 2)
    api.put_native_function(process, _module, u'negate', negate, 1)
    api.put_native_function(process, _module, u'abs', modulo, 1)
    api.put_native_function(process, _module, u'le', le, 2)

    _module.export_all()
    process.classes.add_env(_module)


@complete_native_routine
def _pow(process, routine):
    arg0 = routine.get_arg(0)
    error.affirm_type(arg0, space.isnumber)
    arg1 = routine.get_arg(1)
    error.affirm_type(arg1, space.isnumber)

    return number.power(arg0, arg1)


@complete_native_routine
def add(process, routine):
    arg0 = routine.get_arg(0)
    error.affirm_type(arg0, space.isnumber)
    arg1 = routine.get_arg(1)
    error.affirm_type(arg1, space.isnumber)

    return number.add(arg0, arg1)


@complete_native_routine
def sub(process, routine):
    arg0 = routine.get_arg(0)
    error.affirm_type(arg0, space.isnumber)
    arg1 = routine.get_arg(1)
    error.affirm_type(arg1, space.isnumber)

    return number.sub(arg0, arg1)


@complete_native_routine
def mul(process, routine):
    arg0 = routine.get_arg(0)
    error.affirm_type(arg0, space.isnumber)
    arg1 = routine.get_arg(1)
    error.affirm_type(arg1, space.isnumber)

    return number.mul(arg0, arg1)


@complete_native_routine
def div(process, routine):
    arg0 = routine.get_arg(0)
    error.affirm_type(arg0, space.isnumber)
    arg1 = routine.get_arg(1)
    error.affirm_type(arg1, space.isnumber)

    return number.div(arg0, arg1)


@complete_native_routine
def mod(process, routine):
    arg0 = routine.get_arg(0)
    error.affirm_type(arg0, space.isnumber)
    arg1 = routine.get_arg(1)
    error.affirm_type(arg1, space.isnumber)

    return number.mod(arg0, arg1)


@complete_native_routine
def negate(process, routine):
    arg0 = routine.get_arg(0)
    error.affirm_type(arg0, space.isnumber)

    return number.negate(arg0)

@complete_native_routine
def modulo(process, routine):
    arg0 = routine.get_arg(0)
    error.affirm_type(arg0, space.isnumber)

    return number.modulo(arg0)

@complete_native_routine
def le(process, routine):
    arg0 = routine.get_arg(0)
    error.affirm_type(arg0, space.isnumber)
    arg1 = routine.get_arg(1)
    error.affirm_type(arg1, space.isnumber)

    return number.le(arg0, arg1)
