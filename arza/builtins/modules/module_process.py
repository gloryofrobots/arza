from arza.types import space, api, datatype
from arza.runtime.routine.routine import complete_native_routine


def setup(process, stdlib):
    _module_name = space.newsymbol(process, u'arza:lang:_process')
    _module = space.newemptyenv(_module_name)
    api.put_native_function(process, _module, u'is_idle', is_idle, 1)
    api.put_native_function(process, _module, u'is_active', is_active, 1)
    api.put_native_function(process, _module, u'is_complete', is_complete, 1)
    api.put_native_function(process, _module, u'is_terminated', is_terminated, 1)
    api.put_native_function(process, _module, u'is_finished', is_finished, 1)
    api.put_native_function(process, _module, u'get_active_processes', get_active_processes, 1)
    api.put_native_function(process, _module, u'result', result, 1)

    api.put_native_function(process, _module, u'mailbox', mailbox, 1)
    api.put_native_function(process, _module, u'pop', pop, 1)
    api.put_native_function(process, _module, u'push', push, 2)
    api.put_native_function(process, _module, u'pause', pause, 1)
    api.put_native_function(process, _module, u'resume', resume, 1)
    api.put_native_function(process, _module, u'is_empty', is_empty, 1)
    _module.export_all()
    process.modules.add_module(_module_name, _module)


@complete_native_routine
def is_idle(process, routine):
    pid = routine.get_arg(0)
    return space.newbool(pid.process.is_idle())


@complete_native_routine
def is_active(process, routine):
    pid = routine.get_arg(0)
    return space.newbool(pid.process.is_active())


@complete_native_routine
def is_complete(process, routine):
    pid = routine.get_arg(0)
    return space.newbool(pid.process.is_complete())


@complete_native_routine
def is_terminated(process, routine):
    pid = routine.get_arg(0)
    return space.newbool(pid.process.is_terminated())


@complete_native_routine
def is_finished(process, routine):
    pid = routine.get_arg(0)
    return space.newbool(pid.process.is_finished())


@complete_native_routine
def is_empty(process, routine):
    pid = routine.get_arg(0)
    res = pid.process.mailbox.empty()
    return space.newbool(res)


@complete_native_routine
def __status(process, routine):
    pid = routine.get_arg(0)
    return space.newint(pid.process.state)


@complete_native_routine
def result(process, routine):
    pid = routine.get_arg(0)
    res = pid.process.result
    if res is None:
        return space.newunit()

    return pid.process.result


@complete_native_routine
def mailbox(process, routine):
    pid = routine.get_arg(0)
    return pid.process.mailbox.messages


@complete_native_routine
def pop(process, routine):
    pid = routine.get_arg(0)
    msg = pid.process.mailbox.pop()
    return msg


@complete_native_routine
def push(process, routine):
    msg = routine.get_arg(0)
    pid = routine.get_arg(1)
    # p.mailbox.push(msg)
    pid.process.receive(msg)
    return space.newunit()


@complete_native_routine
def resume(process, routine):
    pid = routine.get_arg(0)
    pid.process.resume()
    return space.newunit()


@complete_native_routine
def get_active_processes(process, routine):
    pid = routine.get_arg(0)
    return pid.process.scheduler.active


@complete_native_routine
def pause(process, routine):
    pid = routine.get_arg(0)
    pid.process.pause()
    return space.newunit()
