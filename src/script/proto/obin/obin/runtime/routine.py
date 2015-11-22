from rpython.rlib import jit

from obin.objects.object_space import _w
from obin.objects.stack import Stack
from obin.runtime.reference import References
from obin.objects.object_space import newstring
from obin.runtime.environment import newenv


class Routine(object):
    class State:
        IDLE = -1
        COMPLETE = 0
        INPROCESS = 2
        TERMINATED = 3
        SUSPENDED = 4

    def __init__(self):
        super(Routine, self).__init__()
        self.process = None
        self.__continuation = None
        self.__state = Routine.State.IDLE
        self.called = None
        self.result = None

    def has_continuation(self):
        return self.__continuation is not None

    def set_continuation(self, continuation):
        # if continuation is self.__continuation:
        #     return

        if self.__continuation:
            print self, "\n**************\n", continuation

        assert not self.__continuation
        self.__continuation = continuation

    def continuation(self):
        return self.__continuation

    def resume(self, value):
        # print "RESUME", self.__state
        assert self.is_suspended()
        self._on_resume(value)
        self.called = None
        self.__state = Routine.State.INPROCESS

    def _on_resume(self, value):
        raise NotImplementedError()

    def inprocess(self):
        assert not self.is_closed()
        self.__state = Routine.State.INPROCESS

    def complete(self, result):
        assert not self.is_closed()
        self.result = result
        self.__state = Routine.State.COMPLETE
        self._on_complete()

    def _on_complete(self):
        raise NotImplementedError()

    def terminate(self, signal):
        assert not self.is_closed()
        assert signal is not None
        self.__state = Routine.State.TERMINATED
        self._on_terminate(signal)

    def _on_terminate(self, signal):
        raise NotImplementedError()

    def activate(self, process):
        assert not self.process
        self.process = process

        self._on_activate()
        self.inprocess()

    def _on_activate(self):
        pass

    def suspend(self):
        assert not self.is_closed()
        self.__state = Routine.State.SUSPENDED

    def execute(self):
        if self.is_complete():
            raise RuntimeError("Already complete")
        self._execute()

    def _execute(self):
        raise NotImplementedError()

    def is_inprocess(self):
        return self.__state == Routine.State.INPROCESS

    def is_idle(self):
        return self.__state == Routine.State.IDLE

    def is_complete(self):
        return self.__state == Routine.State.COMPLETE

    def is_terminated(self):
        return self.__state == Routine.State.TERMINATED

    def is_suspended(self):
        return self.__state == Routine.State.SUSPENDED

    def is_closed(self):
        return self.__state == Routine.State.COMPLETE \
               or self.__state == Routine.State.TERMINATED

    def call_routine(self, routine):
        assert self.process
        self.process.call_routine(routine, self, self)


def complete_native_routine(func):
    def func_wrapper(routine):
        result = func(routine)
        routine.complete(_w(result))

    return func_wrapper


class NativeRoutine(Routine):
    _immutable_fields_ = ['_name_', '_function_']

    def __init__(self, name, function, args, arity):
        super(NativeRoutine, self).__init__()
        from obin.objects.object_space import isstring
        assert isstring(name)
        self._name_ = name
        self._function_ = function
        self.arity = arity
        self.count_args = args.length()
        self._args = args

    # redefine resume because we can call bytecode routine from native and after it resumes as we must complete
    resume = Routine.complete

    def name(self):
        return self._name_.value()

    def get_arg(self, index):
        return self._args.at(index)

    def _execute(self):
        # print "Routine and Ctx", self.__class__.__name__, ctx.__class__.__name__
        self.suspend()
        self._function_(self)

    def _on_complete(self):
        pass
        # self.ctx.stack_append(self.result)

    def to_string(self):
        name = self.name()
        if name is not None:
            return u'function %s() { [native code] }' % (name,)
        else:
            return u'function () { [native code] }'


class BytecodeRoutine(Routine):
    _immutable_fields_ = ['_code_', '_name_', '_stack_size_', '_symbol_size_']

    def __init__(self, name, code, env):
        super(BytecodeRoutine, self).__init__()

        from obin.objects.object_space import isstring
        assert isstring(name)
        self._code_ = code

        self._name_ = name

        self.pc = 0
        self.result = None
        self.env = env

        scope = code.scope
        refs_size = scope.count_refs
        stack_size = code.estimated_stack_size()
        if stack_size:
            self.stack = Stack(stack_size)
        else:
            self.stack = None
        if refs_size != 0:
            self.refs = References(env, refs_size)
        else:
            self.refs = None

    def name(self):
        return self._name_

    def _on_terminate(self, signal):
        self.__signal = signal

    def _on_resume(self, value):
        self.stack.push(value)

    def _on_activate(self):
        pass

    def _on_complete(self):
        pass

    def _execute(self):
        while True:
            if not self.is_inprocess():
                return
            self.__execute()
        pass

    def __execute(self):
        from obin.objects.object_space import object_space
        debug = object_space.interpreter.config.debug
        from obin.runtime.opcodes import BaseJump

        opcode = self.bytecode().get_opcode(self.pc)

        debug = True

        opcode.eval(self)
        if debug:
            d = u'%s\t%s' % (unicode(str(self.pc)), unicode(str(opcode)))
            # d = u'%s' % (unicode(str(pc)))
            d = u'%3d %25s %s ' % (self.pc, unicode(opcode), unicode([unicode(s) for s in self.stack]))

            # print(getattr(self, "_name_", None), str(hex(id(self))), d)

        # RETURN or THROW occured
        if self.is_closed():
            return

        # print "result", self.result
        if isinstance(opcode, BaseJump):
            # print "JUMP"
            new_pc = opcode.do_jump(self, self.pc)
            self.pc = new_pc
            # self._execute()
            # # complete after jump
            # if self.is_complete():
            #     return
        else:
            self.pc += 1

    def bytecode(self):
        return self._code_

    def to_string(self):
        name = self.name()
        if name is not None:
            return u'function %s() { }' % (name,)
        else:
            return u'function () { }'

            # def __repr__(self):
            #     return "%s" % (self.bytecode())


def create_primitive_routine(name, primitive, args, arity):
    return NativeRoutine(name, primitive, args, arity)


def create_module_routine(code, module, _globals):
    if _globals is not None:
        global_env = newenv(_globals, None)
    else:
        global_env = None
    env = newenv(module, global_env)
    return jit.promote(BytecodeRoutine(newstring("__module__"), code, env))


def create_eval_routine(code):
    from obin.runtime.environment import newenv
    obj = code.scope.create_object()
    env = newenv(obj, None)
    return jit.promote(BytecodeRoutine(newstring("__module__"), code, env))


def create_function_routine(func, args, outer_env):
    # TODO CHANGE TO PUBLIC FIELDS
    code = func._bytecode_
    scope = code.scope
    name = func._name_

    env = create_function_environment(func, scope, args, outer_env)
    return jit.promote(BytecodeRoutine(name, code, env))


def create_function_environment(func, scope, args, outer_env):
    from obin.runtime.environment import newenv
    from obin.objects.object_space import newplainobject_with_slots, newvector

    declared_args_count = scope.count_args
    is_variadic = scope.is_variadic
    args_count = args.length()

    if not is_variadic:
        if args_count < declared_args_count:
            raise RuntimeError("Wrong argument count in function call %d < %d %s" % (args_count, declared_args_count,
                                                                                     str(scope.variables.keys())))

        actual_args_count = declared_args_count
        if args_count != actual_args_count:
            raise RuntimeError("Wrong argument count in function call %s %s" %
                               (str(scope.variables.keys()), str(args)))
    else:
        varargs_index = declared_args_count - 1
        actual_args_count = varargs_index

        if args_count < actual_args_count:
            raise RuntimeError("Wrong argument count in function call %d < %d %s" % (args_count, declared_args_count,
                                                                                     str(scope.variables.keys())))

        if args_count != actual_args_count:
            args.fold_slice_into_itself(actual_args_count)
        else:
            args.append(newvector([]))

    slots = scope.create_environment_slots(args)
    env = newenv(newplainobject_with_slots(slots), outer_env)

    fn_index = scope.fn_name_index
    if fn_index != -1:
        env.set_local(fn_index, func)

    return env
