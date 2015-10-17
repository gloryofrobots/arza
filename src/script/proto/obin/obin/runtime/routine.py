from obin.objects.object_space import _w

def get_printable_location(pc, debug, jscode):
    if pc < jscode.opcode_count():
        opcode = jscode.get_opcode(pc)
        if jscode._function_name_ is not None:
            return '%d: %s function: %s' % (pc, str(opcode), str(jscode._function_name_))
        else:
            return '%d: %s' % (pc, str(opcode))
    else:
        return '%d: %s' % (pc, 'end of opcodes')

class Routine(object):
    class State:
        IDLE = -1
        COMPLETE = 0
        INPROCESS = 2
        TERMINATED = 3
        SUSPENDED = 4

    def __init__(self):
        super(Routine, self).__init__()
        self.fiber = None
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

    def clone(self):
        raise NotImplementedError()

    def set_context(self, ctx):
        self.ctx = ctx
        if self.ctx.routine() == self:
            return

        self.ctx.set_routine(self)

    def stack_start_index(self):
        return self.__stack_start_index

    def set_start_stack_index(self, start_index):
        self.__stack_start_index = start_index

    def set_finalizer(self, finalizer):
        self.__finalizer = finalizer

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

    def get_finalizer(self):
        return self.__finalizer

    def has_continuation(self):
        return self.__continuation is not None

    def set_continuation(self, continuation):
        if self.__continuation:
            print self, continuation
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

    def is_complete(self):
        return self.__state == Routine.State.COMPLETE

    def is_terminated(self):
        return self.__state == Routine.State.TERMINATED

    def is_suspended(self):
        return self.__state == Routine.State.SUSPENDED

    def is_closed(self):
        return self.__state == Routine.State.COMPLETE \
               or self.__state == Routine.State.TERMINATED

    def activate(self, fiber):
        assert not self.fiber
        self.fiber = fiber

        self._on_activate()

    def is_block(self):
        return False

    def is_function_code(self):
        return False

    def _on_activate(self):
        pass

    def call_routine(self, routine):
        assert self.fiber
        self.fiber.call_routine(routine, self)

    def execute(self):
        if self.is_complete():
            raise RuntimeError("Already complete")
        self._execute()

    def _execute(self):
        raise NotImplementedError()


class BaseRoutine(Routine):
    _settled_ = True
    eval_code = False
    function_code = False
    configurable_bindings = False

    def estimated_stack_size(self):
        return 2

    def to_string(self):
        return u'function() {}'

    def variables(self):
        return []

    def functions(self):
        return []

    def params(self):
        return []

    def name(self):
        return '_unnamed_'

    def is_function_code(self):
        return False

    def env_size(self):
        return 0

def complete_native_routine(func):
   def func_wrapper(ctx, routine):
       result = func(ctx, routine)
       routine.complete(_w(result))

   return func_wrapper

class NativeRoutine(BaseRoutine):
    _immutable_fields_ = ['_name_', '_function_']

    def __init__(self, function, name=u''):
        super(NativeRoutine, self).__init__()

        assert isinstance(name, unicode)
        self._name_ = name
        self._function_ = function

    def clone(self):
        return NativeRoutine(self._function_, self._name_)

    #redefine resume because we can call bytecode routine from native and after it resumes as we must complete
    resume = Routine.complete

    # def resume(self, value):
    #     # print "RESUME", self.__state
    #     assert self.is_suspended()
    #     self.called = None
    #     self.complete(value)

    def name(self):
        return self._name_

    def args(self):
        args = self.ctx.argv()
        this = self.ctx.this_binding()
        return this, args

    def _execute(self):
        #print "Routine and Ctx", self.__class__.__name__, ctx.__class__.__name__
        self.suspend()
        self._function_(self.ctx, self)

    def _on_complete(self):
        self.ctx.stack_append(self.result)

    def to_string(self):
        name = self.name()
        if name is not None:
            return u'function %s() { [native code] }' % (name, )
        else:
            return u'function () { [native code] }'


class BytecodeRoutine(BaseRoutine):
    _immutable_fields_ = ['_js_code_', '_stack_size_', '_symbol_size_']

    def __init__(self, js_code):
        super(BytecodeRoutine, self).__init__()
        from obin.compile.code import Code
        assert isinstance(js_code, Code)
        self._js_code_ = js_code
        if not self._js_code_.is_compiled():
            self._js_code_.emit('LOAD_UNDEFINED')
            self._js_code_.compile()

        self._stack_size_ = js_code.estimated_stack_size()
        self._symbol_size_ = js_code.symbol_size()
        self.pc = 0
        self.result = None

    def _on_activate(self):
        assert self.ctx
        if self.stack_start_index() is not None:
            self.ctx._set_stack_pointer(self.stack_start_index())

    def clone(self):
        return BytecodeRoutine(self._js_code_)

    def code(self):
        return self._js_code_

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
        opcode.eval(self.ctx)

        #RETURN or THROW occured
        if self.is_closed():
            return

        #print "result", self.result
        debug = True
        if debug:
            d = u'%s\t%s' % (unicode(str(self.pc)), unicode(str(opcode)))
            #d = u'%s' % (unicode(str(pc)))
            #d = u'%3d %25s %s %s' % (pc, unicode(opcode), unicode([unicode(s) for s in ctx._stack_]), unicode(result))

            # print(getattr(self, "_name_", None), str(hex(id(self))), d)
        if isinstance(opcode, BaseJump):
            #print "JUMP"
            new_pc = opcode.do_jump(self.ctx, self.pc)
            self.pc = new_pc
            # self._execute()
            # # complete after jump
            # if self.is_complete():
            #     return
        else:
            self.pc += 1

        if self.pc >= self.code().opcode_count():
            #print "_execute", self, self.result
            assert not self.result
            self.complete(self.ctx.stack_top())

    def estimated_stack_size(self):
        return self._stack_size_

    def env_size(self):
        return self._symbol_size_

    def get_js_code(self):
        from obin.compile.code import Code
        assert isinstance(self._js_code_, Code)
        return self._js_code_

    def variables(self):
        code = self.get_js_code()
        return code.variables()

    def functions(self):
        # XXX tuning
        code = self.get_js_code()
        functions = code.functions()
        return functions

    def params(self):
        code = self.get_js_code()
        return code.params()

    def name(self):
        return u'_unnamed_'

    def to_string(self):
        name = self.name()
        if name is not None:
            return u'function %s() { }' % (name, )
        else:
            return u'function () { }'

    def __repr__(self):
        return "%s" % (self.get_js_code())

class GlobalRoutine(BytecodeRoutine):
    def __repr__(self):
        return "Global Routine: %s" % (str(self.get_js_code()))

class FunctionRoutine(BytecodeRoutine):
    _immutable_fields_ = ['_js_code_', '_stack_size_', '_symbol_size_', '_name_']

    def __init__(self, name, js_code):
        assert isinstance(name, unicode)
        BytecodeRoutine.__init__(self, js_code)
        js_code._function_name_ = name
        self._name_ = name

    def clone(self):
        return FunctionRoutine(self._name_, self._js_code_)

    def name(self):
        return self._name_

    def is_function_code(self):
        return True

    def __repr__(self):
        return "function %s {}" % self.name()

class BlockRoutine(BytecodeRoutine):
    _immutable_fields_ = ['_js_code_', '_stack_size_', '_symbol_size_', '_signal_name_']

    def __init__(self, _signal_name_, js_code):
        BytecodeRoutine.__init__(self, js_code)
        self._signal_name_ = _signal_name_

    def clone(self):
        return BlockRoutine(self._signal_name_, self._js_code_)

    def is_block(self):
        return True

    def signal_name(self):
        return self._signal_name_

    def _on_force_complete(self):
        self.fiber.complete_last_routine(self.result)
