from arza.types import number, space, api
from arza.runtime.routine.routine import complete_native_routine
from arza.runtime import error


def setup(process, stdlib):
    _module_name = space.newsymbol(process, u'arza:lang:_bit')
    _module = space.newemptyenv(_module_name)
    api.put_native_function(process, _module, u'bitnot', bitnot, 1)
    api.put_native_function(process, _module, u'bitor', bitor, 2)
    api.put_native_function(process, _module, u'bitxor', bitxor, 2)
    api.put_native_function(process, _module, u'bitand', bitand, 2)
    api.put_native_function(process, _module, u'lshift', lshift, 2)
    api.put_native_function(process, _module, u'rshift', rshift, 2)

    _module.export_all()
    process.modules.add_env(_module)


@complete_native_routine
def bitnot(process, routine):
    arg0 = routine.get_arg(0)
    error.affirm_type(arg0, space.isint)

    return number.bitnot(arg0)


@complete_native_routine
def bitor(process, routine):
    arg0 = routine.get_arg(0)
    error.affirm_type(arg0, space.isint)
    arg1 = routine.get_arg(1)
    error.affirm_type(arg1, space.isint)

    return number.bitor(arg0, arg1)


@complete_native_routine
def bitxor(process, routine):
    arg0 = routine.get_arg(0)
    error.affirm_type(arg0, space.isint)
    arg1 = routine.get_arg(1)
    error.affirm_type(arg1, space.isint)

    return number.bitxor(arg0, arg1)


@complete_native_routine
def bitand(process, routine):
    arg0 = routine.get_arg(0)
    error.affirm_type(arg0, space.isint)
    arg1 = routine.get_arg(1)
    error.affirm_type(arg1, space.isint)

    return number.bitand(arg0, arg1)


@complete_native_routine
def lshift(process, routine):
    arg0 = routine.get_arg(0)
    error.affirm_type(arg0, space.isint)
    arg1 = routine.get_arg(1)
    error.affirm_type(arg1, space.isint)

    return number.lsh(arg0, arg1)


@complete_native_routine
def rshift(process, routine):
    arg0 = routine.get_arg(0)
    error.affirm_type(arg0, space.isint)
    arg1 = routine.get_arg(1)
    error.affirm_type(arg1, space.isint)

    return number.rsh(arg0, arg1)
