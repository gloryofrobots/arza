from arza.types import api, space
from arza.runtime import error
from arza.runtime.routine.routine import complete_native_routine


def setup(process, stdlib):
    name = space.newsymbol(process, u'arza:lang:_io')
    _module = space.newemptyenv(name)
    api.put_native_function(process, _module, u'stdin', _stdin, 0)
    api.put_native_function(process, _module, u'stdout', _stdout, 0)
    api.put_native_function(process, _module, u'stderr', _stderr, 0)
    api.put_native_function(process, _module, u'write', _write, 2)
    _module.export_all()
    process.classes.add_env(_module)


@complete_native_routine
def _stdin(process, routine):
    return process.io.stdin


@complete_native_routine
def _stderr(process, routine):
    return process.io.stderr


@complete_native_routine
def _stdout(process, routine):
    return process.io.stdout


@complete_native_routine
def _write(process, routine):
    val = routine.get_arg(0)
    io = routine.get_arg(1)
    error.affirm_type(io, space.isiodevice)
    io.write(val)
    return space.newunit()
