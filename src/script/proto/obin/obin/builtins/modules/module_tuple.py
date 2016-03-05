__author__ = 'gloryofrobots'
from obin.types import tuples, space, api
from obin.runtime.routine import complete_native_routine

def setup(process,  stdlib):
    _module = space.newemptyenv(space.newsymbol(process, u'_tuple'))
    api.put_native_function(process, _module, u'length', _length, 1)

    _module.export_all()
    process.modules.add_module('_tuple', _module)

@complete_native_routine
def _length(process, routine):
    arg0 = routine.get_arg(0)

    return tuples.length(arg0)