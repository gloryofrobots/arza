
from arza.types import api, space, obj
from arza.runtime import error
from arza.runtime.routine.routine import complete_native_routine


def setup(process, stdlib):
    _class = stdlib.classes.Tuple
    setup_class(process, _class)


def setup_class(process, _class):
    api.put_native_function(process, _class, u'__instance__', instance, 0)


@complete_native_routine
def instance(process, routine):
    arg0 = routine.get_arg(0)
    return obj.newinstance(process, arg0)
