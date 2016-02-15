from obin.types import api, space, tvar

from obin.runtime.routine import complete_native_routine


def setup(process, module, stdlib):
    tvar_module = space.newemptyenv(space.newsymbol(process, u"tvar"))
    api.put_native_function(process, tvar_module, u'read', tvar_read, 1)
    api.put_native_function(process, tvar_module, u'swap', tvar_swap, 2)
    api.put_native_function(process, tvar_module, u'create', tvar_create, 1)
    process.modules.add_module("tvar", tvar_module)


@complete_native_routine
def tvar_create(process, routine):
    val = routine.get_arg(0)
    return space.newtvar(val)


@complete_native_routine
def tvar_read(process, routine):
    var = routine.get_arg(0)
    return tvar.read(var)


@complete_native_routine
def tvar_swap(process, routine):
    var = routine.get_arg(0)
    value = routine.get_arg(1)
    tvar.swap(var, value)
    return var
