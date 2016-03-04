__author__ = 'gloryofrobots'
from obin.types import tupl, space, api
from obin.runtime.routine.routine import complete_native_routine

def setup(process, stdlib):
    _module = space.newemptyenv(space.newsymbol(process, u'_fiber'))
    api.put_native_function(process, _module, u'spawn', _spawn, 1)
    api.put_native_function(process, _module, u'activate', _activate, 2)

    _module.export_all()
    process.modules.add_module('_fiber', _module)

@complete_native_routine
def _spawn(process, routine):
    from obin.types.fiber import newfiber
    y1, y2 = newfiber(process)
    return space.newtuple([y1, y2])


def _activate(process, routine):
    from obin.types.fiber import activate_fiber as activate
    fiber = routine.get_arg(0)
    func = routine.get_arg(1)
    # args = routine.get_arg(2)
    args = space.newtuple([space.newunit()])
    activate(process, fiber, func, args)
    return space.newvoid()
