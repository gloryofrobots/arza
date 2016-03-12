__author__ = 'gloryofrobots'
from obin.types import tuples, space, api
from obin.runtime.routine.routine import complete_native_routine


def setup(process, stdlib):
    _module_name = space.newsymbol(process, u'obin:lang:tuple')
    _module = space.newemptyenv(_module_name)
    api.put_native_function(process, _module, u'length', _length, 1)
    api.put_native_function(process, _module, u'to_list', _to_list, 1)

    _module.export_all()
    process.modules.add_module(_module_name, _module)


@complete_native_routine
def _length(process, routine):
    arg0 = routine.get_arg(0)

    return api.length(arg0)


@complete_native_routine
def _to_list(process, routine):
    arg0 = routine.get_arg(0)

    return tuples.to_list(arg0)
