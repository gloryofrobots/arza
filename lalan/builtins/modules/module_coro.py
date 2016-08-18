from lalan.types import space, api
from lalan.runtime import error
from lalan.runtime.routine.routine import complete_native_routine


def setup(process, stdlib):
    name = space.newsymbol(process, u'lalan:lang:_coro')
    _module = space.newemptyenv(name)
    api.put_native_function(process, _module, u'spawn', _spawn, 1)
    api.put_native_function(process, _module, u'is_complete', _is_complete, 1)
    api.put_native_function(process, _module, u'is_terminated', _is_terminated, 1)
    api.put_native_function(process, _module, u'is_active', _is_active, 1)
    api.put_native_function(process, _module, u'is_passive', _is_passive, 1)
    api.put_native_function(process, _module, u'is_finished', _is_finished, 1)
    api.put_native_function(process, _module, u'is_initialised', _is_initialised, 1)

    _module.export_all()
    process.modules.add_module(name, _module)


@complete_native_routine
def _spawn(process, routine):
    fn = routine.get_arg(0)
    return space.newcoroutine(process, fn)


@complete_native_routine
def _is_initialised(process, routine):
    co = routine.get_arg(0)
    error.affirm_type(co, space.iscoroutine)
    return space.newbool(co.initialised)


@complete_native_routine
def _is_complete(process, routine):
    co = routine.get_arg(0)
    error.affirm_type(co, space.iscoroutine)
    return space.newbool(co.is_complete())


@complete_native_routine
def _is_finished(process, routine):
    co = routine.get_arg(0)
    error.affirm_type(co, space.iscoroutine)
    return space.newbool(co.is_finished())


@complete_native_routine
def _is_terminated(process, routine):
    co = routine.get_arg(0)
    error.affirm_type(co, space.iscoroutine)
    return space.newbool(co.is_terminated())


@complete_native_routine
def _is_active(process, routine):
    co = routine.get_arg(0)
    error.affirm_type(co, space.iscoroutine)
    return space.newbool(co.is_active())


@complete_native_routine
def _is_passive(process, routine):
    co = routine.get_arg(0)
    error.affirm_type(co, space.iscoroutine)
    return space.newbool(co.is_passive())
