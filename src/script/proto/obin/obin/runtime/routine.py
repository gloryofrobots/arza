from obin.objects.object_space import _w
from rpython.rlib import jit
routine_contexts = set()

def get_printable_location(pc, debug, jscode):
    if pc < jscode.opcode_count():
        opcode = jscode.get_opcode(pc)
        if jscode._function_name_ is not None:
            return '%d: %s function: %s' % (pc, str(opcode), str(jscode._function_name_))
        else:
            return '%d: %s' % (pc, str(opcode))
    else:
        return '%d: %s' % (pc, 'end of opcodes')

jitdriver = jit.JitDriver(greens=['pc', 'debug', 'self'], reds=['result', 'ctx'], get_printable_location=get_printable_location, virtualizables=['ctx'])

class Routine(object):
    class State:
        IDLE = -1
        COMPLETE = 0
        INPROCESS = 1
        TERMINATED = 2
        SUSPENDED = 3

    def __init__(self):
        self.fiber = None
        self.__continuation = None
        self.__state = Routine.State.IDLE
        self.called = None
        self.arguments = None
        self.result = None
        self.ctx = None
        self.__signal = None
        self.__signal_handlers = {}

    def add_signal_handler(self, signal, handler):
        self.__signal_handlers[signal] = handler

    def get_signal_handler(self, signal):
        return self.__signal_handlers.get(signal, None)

    def has_continuation(self):
        return self.__continuation is not None

    def continuation(self):
        return self.__continuation

    def signal(self):
        return self.__signal

    def resume(self, value):
        assert self.is_suspended()
        self.result = value
        self.ctx.stack_append(value)
        self.__state = Routine.State.INPROCESS

    def inprocess(self):
        assert not self.is_closed()
        self.__state = Routine.State.INPROCESS

    def complete(self, result):
        assert not self.is_closed()
        self.result = result
        self.__state = Routine.State.COMPLETE

    def terminate(self, signal):
        assert not self.is_closed()
        assert signal is not None
        self.__state = Routine.State.TERMINATED
        self.__signal = signal

    def suspend(self):
        assert not self.is_closed()
        return self.__state == Routine.State.SUSPENDED

    def catch_signal(self):
        assert self.is_terminated()
        # handler = self.get_signal_handler(self.__signal)
        return None

    def is_inprocess(self):
        return self.__state == Routine.State.INPROCESS

    def is_complete(self):
        return self.__state == Routine.State.COMPLETE

    def is_terminated(self):
        return self.__state == Routine.State.TERMINATED

    def is_suspended(self):
        return self.__state == Routine.State.SUSPENDED

    def is_closed(self):
        return self.__state == Routine.State.COMPLETE or self.__state == Routine.State.TERMINATED

    def activate(self, fiber):
        assert not self.fiber
        self.fiber = fiber
        self._on_activate()

    def _on_activate(self):
        pass

    def call_from_fiber(self, fiber):
        self.activate(fiber)

    def call_routine(self, routine):
        assert not self.is_closed()

        if self.called is not None:
            raise RuntimeError("Called has exists")

        self.called = routine
        self.suspend()
        routine.call_from_continuation(self)

    def call_from_continuation(self, routine):
        self.__continuation = routine
        self.call_from_fiber(routine.fiber)

    def execute(self):
        if self.is_complete():
            raise RuntimeError("Already complete")
        self._execute()

    def _execute(self):
        raise NotImplementedError()


class BaseRoutine(object):
    _settled_ = True
    eval_code = False
    function_code = False
    configurable_bindings = False

    def run(self, ctx):
        raise NotImplementedError

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

    def is_eval_code(self):
        return False

    def is_function_code(self):
        return False

    def env_size(self):
        return 0


class NativeRoutine(BaseRoutine):
    _immutable_fields_ = ['_name_', '_function_']

    def __init__(self, function, name=u''):
        super(NativeRoutine, self).__init__()

        assert isinstance(name, unicode)
        self._name_ = name
        self._function_ = function

    def name(self):
        return self._name_

    def run(self, ctx):
        routine_contexts.add((self.__class__.__name__, ctx.__class__.__name__))
        #print "Routine and Ctx", self.__class__.__name__, ctx.__class__.__name__

        from obin.runtime.completion import ReturnCompletion

        args = ctx.argv()
        this = ctx.this_binding()
        assert isinstance(self, NativeRoutine)
        res = self._function_(this, args)
        w_res = _w(res)
        compl = ReturnCompletion(value=w_res)
        return compl

    def to_string(self):
        name = self.name()
        if name is not None:
            return u'function %s() { [native code] }' % (name, )
        else:
            return u'function () { [native code] }'


class NativeIntimateRoutine(NativeRoutine):
    _immutable_fields_ = ['_name_', '_intimate_function_']

    def __init__(self, function, name=u''):
        assert isinstance(name, unicode)
        self._name_ = name
        self._intimate_function_ = function

    def run(self, ctx):
        routine_contexts.add((self.__class__.__name__, ctx.__class__.__name__))
        # print "Routine and Ctx", self.__class__.__name__, ctx.__class__.__name__
        from obin.runtime.completion import Completion
        compl = self._intimate_function_(ctx)
        assert isinstance(compl, Completion)
        return compl


class BytecodeRoutine(BaseRoutine):
    _immutable_fields_ = ['_js_code_', '_stack_size_', '_symbol_size_']

    def __init__(self, js_code):
        from obin.compile.code import Code
        assert isinstance(js_code, Code)
        self._js_code_ = js_code
        self._js_code_.compile()
        self._stack_size_ = js_code.estimated_stack_size()
        self._symbol_size_ = js_code.symbol_size()
        self.pc = 0
        self.result = None


    def __run(self, ctx):
        routine_contexts.add((self.__class__.__name__, ctx.__class__.__name__))
        # print "Routine and Ctx", self.__class__.__name__, ctx.__class__.__name__
        from obin.objects.object_space import object_space
        debug = object_space.interpreter.config.debug
        from obin.runtime.completion import NormalCompletion, is_return_completion, is_empty_completion, is_completion
        from obin.runtime.opcodes import BaseJump
        code = self._js_code_

        if code.opcode_count() == 0:
            return NormalCompletion()

        if debug:
            print('start running %s' % (str(self)))

        self.pc = 0
        self.result = None
        while True:
            if self.pc >= code.opcode_count():
                break
            opcode = code.get_opcode(self.pc)
            self.result = opcode.eval(ctx)

            if debug:
                d = u'%s\t%s' % (unicode(str(self.pc)), unicode(str(opcode)))
                #d = u'%s' % (unicode(str(pc)))
                #d = u'%3d %25s %s %s' % (pc, unicode(opcode), unicode([unicode(s) for s in ctx._stack_]), unicode(result))
                print(d)

            if is_return_completion(self.result):
                break
            elif not is_completion(self.result):
                self.result = NormalCompletion()

            if isinstance(opcode, BaseJump):
                new_pc = opcode.do_jump(ctx, self.pc)
                self.pc = new_pc
                continue
            else:
                self.pc += 1

        if self.result is None or is_empty_completion(self.result):
            self.result = NormalCompletion(value=ctx.stack_top())

        return self.result

    def code(self):
        return self._js_code_

    def _execute(self, ctx):
        from obin.objects.object_space import object_space
        debug = object_space.interpreter.config.debug
        from obin.runtime.completion import NormalCompletion, is_return_completion, is_empty_completion, is_completion
        from obin.runtime.opcodes import BaseJump

        if self.pc >= self.code().opcode_count():
            return

        opcode = self.code().get_opcode(self.pc)
        self.result = opcode.eval(ctx)
        #print "result", self.result
        if debug:
            d = u'%s\t%s' % (unicode(str(self.pc)), unicode(str(opcode)))
            #d = u'%s' % (unicode(str(pc)))
            #d = u'%3d %25s %s %s' % (pc, unicode(opcode), unicode([unicode(s) for s in ctx._stack_]), unicode(result))
            print(d)
        if isinstance(opcode, BaseJump):
            #print "JUMP"
            new_pc = opcode.do_jump(ctx, self.pc)
            self.pc = new_pc
            self._execute(ctx)
        else:
            self.pc += 1

    def run(self, ctx):
        routine_contexts.add((self.__class__.__name__, ctx.__class__.__name__))
        # print "Routine and Ctx", self.__class__.__name__, ctx.__class__.__name__
        from obin.objects.object_space import object_space
        debug = object_space.interpreter.config.debug
        from obin.runtime.completion import NormalCompletion, is_return_completion, is_empty_completion, is_completion
        code = self._js_code_

        if code.opcode_count() == 0:
            return NormalCompletion()

        if debug:
            print('start running %s' % (str(self)))

        self.pc = 0
        self.result = None

        while True:
            if self.pc >= code.opcode_count():
                break

            self._execute(ctx)

            if is_return_completion(self.result):
                break

        if self.result is None or is_empty_completion(self.result):
            self.result = NormalCompletion(value=ctx.stack_top())

        return self.result

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
     pass


class EvalRoutine(BytecodeRoutine):
    def is_eval_code(self):
        return True


class FunctionRoutine(BytecodeRoutine):
    _immutable_fields_ = ['_js_code_', '_stack_size_', '_symbol_size_', '_name_']

    def __init__(self, name, js_code):
        assert isinstance(name, unicode)
        BytecodeRoutine.__init__(self, js_code)
        js_code._function_name_ = name
        self._name_ = name

    def name(self):
        return self._name_

    def is_function_code(self):
        return True
