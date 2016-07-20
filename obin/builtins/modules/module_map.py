from obin.types import pmap, space, api
from obin.runtime.routine.routine import complete_native_routine
from obin.runtime import error


def setup(process, stdlib):
    _module_name = space.newsymbol(process, u'obin:lang:_map')
    _module = space.newemptyenv(_module_name)
    api.put_native_function(process, _module, u'to_list', _to_list, 1)

    _module.export_all()
    process.modules.add_module(_module_name, _module)


@complete_native_routine
def _to_list(process, routine):
    arg0 = routine.get_arg(0)

    return pmap.to_list(arg0)
