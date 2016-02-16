__author__ = 'gloryofrobots'
__author__ = 'gloryofrobots'
from obin.types import tupl, space, api
from obin.runtime.routine import complete_native_routine

def setup(process, module, stdlib):
    _module = space.newemptyenv(space.newsymbol(process, u'_tuples'))
    api.put_native_function(process, _module, u'length', _length, 1)

    process.modules.add_module('_tuples', _module)

@complete_native_routine
def _length(process, routine):
    arg0 = routine.get_arg(0)

    return tupl.length(arg0)