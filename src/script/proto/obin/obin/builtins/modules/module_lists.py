__author__ = 'gloryofrobots'
from obin.types import plist, space, api
from obin.runtime.routine import complete_native_routine


def setup(process, module, stdlib):
    _module = space.newemptyenv(space.newsymbol(process, u'lists'))
    api.put_native_function(process, _module, u'tail', _tail, 1)
    api.put_native_function(process, _module, u'empty', _empty, 0)
    api.put_native_function(process, _module, u'is_empty', _is_empty, 1)
    api.put_native_function(process, _module, u'head', _head, 1)
    api.put_native_function(process, _module, u'cons', _cons, 2)

    process.modules.add_module('lists', _module)


@complete_native_routine
def _tail(process, routine):
    arg0 = routine.get_arg(0)

    return plist.tail(arg0)


@complete_native_routine
def _empty(process, routine):
    return plist.empty()


@complete_native_routine
def _is_empty(process, routine):
    arg0 = routine.get_arg(0)

    return space.newbool(plist.is_empty(arg0))


@complete_native_routine
def _head(process, routine):
    arg0 = routine.get_arg(0)

    return plist.head(arg0)


@complete_native_routine
def _cons(process, routine):
    arg0 = routine.get_arg(0)
    arg1 = routine.get_arg(1)

    return plist.cons(arg0, arg1)
