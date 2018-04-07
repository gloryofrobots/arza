from arza.types import api, space, objects
from arza.runtime import error
from arza.runtime.routine.routine import complete_native_routine


def setup(process, stdlib):
    _class = stdlib.classes.Class
    setup_class(process, _class)


def setup_class(process, _class):
    api.put_native_function(process, _class, u'__instance__', instance, 0)


@complete_native_routine
def instance(process, routine):
    arg0 = routine.get_arg(0)
    return objects.newinstance(process, arg0)
