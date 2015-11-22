from obin.objects.object_space import _w


def complete_native_routine(func):
    def func_wrapper(routine):
        result = func(routine)
        routine.complete(_w(result))

    return func_wrapper


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

    # called in RETURN
    def force_complete(self, result):
        self.complete(result)
        self._on_force_complete()

    def _on_force_complete(self):
        raise NotImplementedError()

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

    def is_block(self):
        return False

    def call_routine(self, routine):
        assert self.process
        self.process.call_routine(routine, self, self)


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

    def __init__(self, code, name):
        super(BytecodeRoutine, self).__init__()

        from obin.objects.object_space import isstring
        assert isstring(name)

        self.ctx = None
        self.__signal = None
        self.__signal_handlers = {}
        self.__stack_start_index = None

        self._code_ = code

        self._name_ = name

        scope = code.scope
        self._refs_size_ = scope.count_refs
        self._env_size_ = scope.count_vars
        self._stack_size_ = code.estimated_stack_size()
        self.pc = 0
        self.result = None

    def signal(self):
        return self.__signal

    def catch_signal(self, signal):
        handler = self.get_signal_handler(self.__signal)
        return handler

    def stack_top(self):
        return self.ctx.stack_top()
        pass

    def set_context(self, ctx):
        assert not self.ctx
        self.ctx = ctx

    def stack_start_index(self):
        return self.__stack_start_index

    # def set_start_stack_index(self, start_index):
    #     self.__stack_start_index = start_index

    def add_signal_handler(self, signal, handler):
        self.__signal_handlers[signal] = handler

    def get_signal_handler(self, signal):
        from obin.objects.object_space import iskindof

        if not len(self.__signal_handlers):
            return None

        for catchedsignal in self.__signal_handlers:
            # if iskindof(catchedsignal, signal):

            #     return self.__signal_handlers[catchedsignal]
            return self.__signal_handlers[catchedsignal]

    def name(self):
        return self._name_

    def _on_terminate(self, signal):
        self.__signal = signal

    def _on_resume(self, value):
        self.ctx.stack_append(value)

    def _on_activate(self):
        assert self.ctx
        if self.stack_start_index() is not None:
            self.ctx.set_stack_pointer(self.stack_start_index())

    def _on_complete(self):
        pass

    def _on_force_complete(self):
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

        opcode.eval(self.ctx)
        if debug:
            d = u'%s\t%s' % (unicode(str(self.pc)), unicode(str(opcode)))
            # d = u'%s' % (unicode(str(pc)))
            d = u'%3d %25s %s ' % (self.pc, unicode(opcode), unicode([unicode(s) for s in self.ctx.stack]))

            # print(getattr(self, "_name_", None), str(hex(id(self))), d)

        # RETURN or THROW occured
        if self.is_closed():
            return

        # print "result", self.result
        if isinstance(opcode, BaseJump):
            # print "JUMP"
            new_pc = opcode.do_jump(self.ctx, self.pc)
            self.pc = new_pc
            # self._execute()
            # # complete after jump
            # if self.is_complete():
            #     return
        else:
            self.pc += 1

    def estimated_stack_size(self):
        return self._stack_size_

    def estimated_refs_count(self):
        return self._refs_size_

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

def create_native_routine(name, primitive, args, arity):
    return NativeRoutine(name, primitive, args, arity)

def create_function_routine(code, name):
    return BytecodeRoutine(code, name)

def create_bytecode_routine(code):
    from obin.objects.object_space import newstring
    return BytecodeRoutine(code, newstring("UNNAMED"))


class BlockRoutine(BytecodeRoutine):
    _immutable_fields_ = ['_code_', '_stack_size_', '_symbol_size_', '_signal_name_']

    def __init__(self, _signal_name_, code):
        from obin.objects.object_space import newstring
        BytecodeRoutine.__init__(self, code, newstring("BLOCK"))
        self._signal_name_ = _signal_name_

    def is_block(self):
        return True

    def signal_name(self):
        return self._signal_name_

    def _on_force_complete(self):
        self.process.complete_last_routine(self.result)
