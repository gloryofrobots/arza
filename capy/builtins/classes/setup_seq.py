
from capy.types import api, space
from capy.runtime import error
from capy.runtime.routine.routine import complete_native_routine


def setup(process, stdlib):
    _class = stdlib.classes.Seq
    setup_class(process, _class)


def setup_class(process, _class):
    api.put_native_method(process, _class, u'head', _head, 1)
    api.put_native_method(process, _class, u'tail', _tail, 1)


@complete_native_routine
def _head(process, routine):
    arg0 = routine.get_arg(0)

    return api.head(arg0)


@complete_native_routine
def _tail(process, routine):
    arg0 = routine.get_arg(0)

    return api.tail(arg0)
