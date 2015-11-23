__author__ = 'gloryofrobots'

from obin.objects.stack import Stack
from obin.runtime.reference import References

from obin.runtime.routine.base import BaseRoutine



class BytecodeRoutine(BaseRoutine):
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
        self.literals = scope.literals
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


