

from capy.types import number, space, api
from capy.runtime import error
from capy.runtime.routine.routine import complete_native_routine


def setup(process, stdlib):
    _class = stdlib.classes.Number
    setup_class(process, _class)


def setup_class(process, _class):
    api.put_native_method(process, _class, u'__pow__', _pow, 2)
    api.put_native_method(process, _class, u'__add__', add, 2)
    api.put_native_method(process, _class, u'__sub__', sub, 2)
    api.put_native_method(process, _class, u'__mul__', mul, 2)
    api.put_native_method(process, _class, u'__div__', div, 2)
    api.put_native_method(process, _class, u'__mod__', mod, 2)
    api.put_native_method(process, _class, u'__neg__', negate, 1)
    api.put_native_method(process, _class, u'__abs__', modulo, 1)
    api.put_native_method(process, _class, u'__le__', le, 2)
    api.put_native_method(process, _class, u'__lt__', lt, 2)
    api.put_native_method(process, _class, u'__ge__', ge, 2)
    api.put_native_method(process, _class, u'__gt__', gt, 2)
    api.put_native_method(process, _class, u'__bnot__', bitnot, 1)
    api.put_native_method(process, _class, u'__bor__', bitor, 2)
    api.put_native_method(process, _class, u'__bxor__', bitxor, 2)
    api.put_native_method(process, _class, u'__band__', bitand, 2)
    api.put_native_method(process, _class, u'__blsh__', lshift, 2)
    api.put_native_method(process, _class, u'__brsh__', rshift, 2)

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

@complete_native_routine
def ge(process, routine):
    arg0 = routine.get_arg(0)
    error.affirm_type(arg0, space.isnumber)
    arg1 = routine.get_arg(1)
    error.affirm_type(arg1, space.isnumber)

    return number.ge(arg0, arg1)

@complete_native_routine
def gt(process, routine):
    arg0 = routine.get_arg(0)
    error.affirm_type(arg0, space.isnumber)
    arg1 = routine.get_arg(1)
    error.affirm_type(arg1, space.isnumber)

    return number.gt(arg0, arg1)

@complete_native_routine
def lt(process, routine):
    arg0 = routine.get_arg(0)
    error.affirm_type(arg0, space.isnumber)
    arg1 = routine.get_arg(1)
    error.affirm_type(arg1, space.isnumber)

    return number.lt(arg0, arg1)

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
