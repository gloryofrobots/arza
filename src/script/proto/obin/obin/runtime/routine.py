from obin.objects.object_space import _w


def complete_native_routine(func):
    def func_wrapper(ctx, routine):
        result = func(ctx, routine)
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
        self.arguments = None
        self.result = None
        self.ctx = None
        self.__signal = None
        self.__signal_handlers = {}
        self.__stack_start_index = None

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

    def signal(self):
        return self.__signal

    def resume(self, value):
        # print "RESUME", self.__state
        assert self.is_suspended()
        self.called = None
        self.ctx.stack_append(value)
        self.__state = Routine.State.INPROCESS

    def inprocess(self):
        assert not self.is_closed()
        self.__state = Routine.State.INPROCESS

    # called in RETURN
    def force_complete(self, result):
        self.complete(result)
        self._on_force_complete()

    def _on_force_complete(self):
        pass

    def complete(self, result):
        assert not self.is_closed()
        self.result = result
        self.__state = Routine.State.COMPLETE
        self._on_complete()

    def _on_complete(self):
        pass

    def terminate(self, signal):
        assert not self.is_closed()
        assert signal is not None
        self.__state = Routine.State.TERMINATED
        self.__signal = signal

    def suspend(self):
        assert not self.is_closed()
        self.__state = Routine.State.SUSPENDED

    def catch_signal(self, signal):
        handler = self.get_signal_handler(self.__signal)
        return handler

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

    def activate(self, process):
        assert not self.process
        self.process = process

        self._on_activate()
        self.inprocess()

    def is_block(self):
        return False

    def _on_activate(self):
        pass

    def call_routine(self, routine):
        assert self.process
        self.process.call_routine(routine, self, self)

    def execute(self):
        if self.is_complete():
            raise RuntimeError("Already complete")
        self._execute()

    def _execute(self):
        raise NotImplementedError()

    def estimated_stack_size(self):
        raise NotImplementedError()

    def env_size(self):
        raise NotImplementedError()


class NativeRoutine(Routine):
    _immutable_fields_ = ['_name_', '_function_']

    def __init__(self, name, function):
        super(NativeRoutine, self).__init__()
        from obin.objects.object_space import isstring
        assert isstring(name)
        self._name_ = name
        self._function_ = function

    # redefine resume because we can call bytecode routine from native and after it resumes as we must complete
    resume = Routine.complete

    def name(self):
        return self._name_.value()

    def args(self):
        args = self.ctx.argv()

        return args

    def method_args(self):
        args = self.ctx.argv()

        return args[0], args[1:]

    def _execute(self):
        # print "Routine and Ctx", self.__class__.__name__, ctx.__class__.__name__
        self.suspend()
        self._function_(self.ctx, self)

    def _on_complete(self):
        self.ctx.stack_append(self.result)

    def to_string(self):
        name = self.name()
        if name is not None:
            return u'function %s() { [native code] }' % (name,)
        else:
            return u'function () { [native code] }'

    def estimated_stack_size(self):
        return 2

    def env_size(self):
        return 0


class BytecodeRoutine(Routine):
    _immutable_fields_ = ['_code_', '_name_', '_stack_size_', '_symbol_size_']

    def __init__(self, code, name):
        super(BytecodeRoutine, self).__init__()

        from obin.objects.object_space import isstring
        assert isstring(name)

        self._code_ = code

        self._name_ = name

        if not self._code_.is_compiled():
            self._code_.emit('LOAD_UNDEFINED')
            self._code_.compile()

        self._stack_size_ = code.estimated_stack_size()
        self._symbol_size_ = code.symbol_size()
        self.pc = 0
        self.result = None

    def name(self):
        return self._name_

    def _on_activate(self):
        assert self.ctx
        if self.stack_start_index() is not None:
            self.ctx.set_stack_pointer(self.stack_start_index())

    def code(self):
        return self._code_

    def _execute(self):
        from obin.objects.object_space import object_space
        debug = object_space.interpreter.config.debug
        from obin.runtime.opcodes import BaseJump

        if self.pc >= self.code().opcode_count():
            self.complete(_w(None))
            return

        # if getattr(self, "_signal_name_", None) == "FINALLY":
        #     print ""
        opcode = self.code().get_opcode(self.pc)

        debug = True
        if debug:
            d = u'%s\t%s' % (unicode(str(self.pc)), unicode(str(opcode)))
            # d = u'%s' % (unicode(str(pc)))
            d = u'%3d %25s %s ' % (self.pc, unicode(opcode), unicode([unicode(s) for s in self.ctx._stack_]))

            # print(getattr(self, "_name_", None), str(hex(id(self))), d)

        opcode.eval(self.ctx)

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

        if self.pc >= self.code().opcode_count():
            # print "_execute", self, self.result
            assert not self.result
            self.complete(self.ctx.stack_top())

    def estimated_stack_size(self):
        return self._stack_size_

    def env_size(self):
        return self._symbol_size_

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
