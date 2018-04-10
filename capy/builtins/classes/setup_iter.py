
from capy.types import api, space
from capy.runtime import error
from capy.runtime.routine.routine import complete_native_routine
from capy.builtins.classes.setup_object import _true, _self


def setup(process, stdlib):
    _class = stdlib.classes.Iter
    setup_class(process, _class)


def setup_class(process, _class):
    api.put_native_method(process, _class, u'value', _value, 1)
    api.put_native_method(process, _class, u'next', _next, 1)
    api.put_native_method(process, _class, u'is_iter', _true, 1)


@complete_native_routine
def _value(process, routine):
    arg0 = routine.get_arg(0)

    return api.value(arg0)


@complete_native_routine
def _next(process, routine):
    arg0 = routine.get_arg(0)

    return api.next(arg0)
