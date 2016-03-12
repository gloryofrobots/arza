__author__ = 'gloryofrobots'
from obin.types import tuples, space, api
from obin.runtime.routine.routine import complete_native_routine

def setup(process,  stdlib):
    name = space.newsymbol(process, u'_tuple')
    _module = space.newemptyenv(name)
    api.put_native_function(process, _module, u'length', _length, 1)

    _module.export_all()
    process.modules.add_module(name, _module)

@complete_native_routine
def _length(process, routine):
    arg0 = routine.get_arg(0)

    return tuples.length(arg0)