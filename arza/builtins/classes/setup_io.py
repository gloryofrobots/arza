
from arza.types import api, space
from arza.runtime import error
from arza.runtime.routine.routine import complete_native_routine


def setup(process, stdlib):
    _file = stdlib.classes.File
    api.put_native_method(process, _file, u'write', _write, 2)
    _io = stdlib.classes.IO
    api.put_native_method(process, _io, u'stdin', _stdin, 0)
    api.put_native_method(process, _io, u'stdout', _stdout, 0)
    api.put_native_method(process, _io, u'stderr', _stderr, 0)


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
    val = routine.get_arg(1)
    io = routine.get_arg(0)
    error.affirm_type(io, space.isiodevice)
    io.write(val)
    return space.newnil()
