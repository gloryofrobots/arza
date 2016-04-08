__author__ = 'gloryofrobots'
from obin.types import tuples, space, api, fiber
from obin.runtime.routine.routine import complete_native_routine

def setup(process, stdlib):
    name = space.newsymbol(process, u'_fiber')
    _module = space.newemptyenv(name)
    api.put_native_function(process, _module, u'spawn', _spawn, 1)
    api.put_native_function(process, _module, u'activate', _activate, 2)
    api.put_native_function(process, _module, u'coroutine', _coroutine, 1)

    _module.export_all()
    process.modules.add_module(name, _module)

@complete_native_routine
def _spawn(process, routine):
    y1, y2 = fiber.newfiber(process)
    return space.newtuple([y1, y2])


@complete_native_routine
def _activate(process, routine):
    fiber = routine.get_arg(0)
    func = routine.get_arg(1)
    args = space.newtuple([space.newunit()])
    fiber.activate_fiber(process, fiber, func, args)
    return space.newvoid()

@complete_native_routine
def _coroutine(process, routine):
    fn = routine.get_arg(0)
    return fiber.newcoroutine(process, fn)
    # y1, y2 = fiber.newfiber(process)
    # return space.newtuple([y1, y2])
