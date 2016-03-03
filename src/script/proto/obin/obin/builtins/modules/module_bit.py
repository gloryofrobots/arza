from obin.types import number, space, api
from obin.runtime.routine.routine import complete_native_routine
from obin.runtime import error



def setup(process, stdlib):
    _module = space.newemptyenv(space.newsymbol(process, u'_bit'))
    api.put_native_function(process, _module, u'bitnot', bitnot, 1)
    api.put_native_function(process, _module, u'bitor', bitor, 2)
    api.put_native_function(process, _module, u'bitxor', bitxor, 2)
    api.put_native_function(process, _module, u'bitand', bitand, 2)
    api.put_native_function(process, _module, u'lshift', lshift, 2)
    api.put_native_function(process, _module, u'rshift', rshift, 2)

    _module.export_all()
    process.modules.add_module('_bit', _module)

@complete_native_routine
def bitnot(process, routine):
    arg0 = routine.get_arg(0)
    error.affirm_type(arg0, space.isint)

    return number.bitnot_i(arg0)


@complete_native_routine
def bitor(process, routine):
    arg0 = routine.get_arg(0)
    error.affirm_type(arg0, space.isint)
    arg1 = routine.get_arg(1)
    error.affirm_type(arg1, space.isint)

    return number.bitor_i_i(arg0, arg1)


@complete_native_routine
def bitxor(process, routine):
    arg0 = routine.get_arg(0)
    error.affirm_type(arg0, space.isint)
    arg1 = routine.get_arg(1)
    error.affirm_type(arg1, space.isint)

    return number.bitxor_i_i(arg0, arg1)


@complete_native_routine
def bitand(process, routine):
    arg0 = routine.get_arg(0)
    error.affirm_type(arg0, space.isint)
    arg1 = routine.get_arg(1)
    error.affirm_type(arg1, space.isint)

    return number.bitand_i_i(arg0, arg1)


@complete_native_routine
def lshift(process, routine):
    arg0 = routine.get_arg(0)
    error.affirm_type(arg0, space.isint)
    arg1 = routine.get_arg(1)
    error.affirm_type(arg1, space.isint)

    return number.lsh_i_i(arg0, arg1)


@complete_native_routine
def rshift(process, routine):
    arg0 = routine.get_arg(0)
    error.affirm_type(arg0, space.isint)
    arg1 = routine.get_arg(1)
    error.affirm_type(arg1, space.isint)

    return number.rsh_i_i(arg0, arg1)