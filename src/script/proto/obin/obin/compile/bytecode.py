#from pypy.rlib.jit import hint
#from pypy.rlib.objectmodel import we_are_translated
from rpython.rlib import jit
from obin.runtime.exception import ObinRuntimeError, ObinSyntaxError

from obin.runtime.opcodes import opcodes, LABEL, BaseJump
from obin.objects.object import W_String


class ByteCode(object):
    _immutable_fields_ = ['compiled_opcodes[*]', '_symbols', 'parameters[*]']

    """ That object stands for code of a single javascript function
    """
    def __init__(self):
        self.opcodes = []
        self.label_count = 0
        self.has_labels = True
        self.startlooplabel = []
        self.endlooplabel = []
        self.pop_after_break = []
        self.updatelooplabel = []
        self._estimated_stack_size = -1
        self._symbols = None
        self.parameters = None
        self._function_name_ = None
        self.compiled_opcodes = None

    def set_symbols(self, symbols):
        self._symbols = symbols
        self.parameters = symbols.parameters[:]

    def index_for_symbol(self, symbol):
        return self._symbols.get_index(symbol)

    def symbols(self):
        return self._symbols.get_symbols()

    def params(self):
        return self._symbols.parameters

    def params_rest(self):
        return self._symbols.rest

    @jit.elidable
    def estimated_stack_size(self):
        if self._estimated_stack_size == -1:
            max_size = 0
            moving_size = 0
            for opcode in self.compiled_opcodes:
                moving_size += opcode.stack_change()
                max_size = max(moving_size, max_size)
            assert max_size >= 0
            self._estimated_stack_size = max_size

        return jit.promote(self._estimated_stack_size)

    def symbol_size(self):
        return self._symbols.len()

    def emit_label(self, num=-1):
        if num == -1:
            num = self.prealocate_label()
        self.emit('LABEL', num)
        return num

    def emit_startloop_label(self):
        num = self.emit_label()
        self.startlooplabel.append(num)
        return num

    def prealocate_label(self):
        num = self.label_count
        self.label_count += 1
        return num

    def prealocate_endloop_label(self, pop_after_break=False):
        num = self.prealocate_label()
        self.endlooplabel.append(num)
        self.pop_after_break.append(pop_after_break)
        return num

    def prealocate_updateloop_label(self):
        num = self.prealocate_label()
        self.updatelooplabel.append(num)
        return num

    def emit_endloop_label(self, label):
        self.endlooplabel.pop()
        self.startlooplabel.pop()
        self.pop_after_break.pop()
        self.emit_label(label)

    def emit_updateloop_label(self, label):
        self.updatelooplabel.pop()
        self.emit_label(label)

    def emit_break(self):
        if not self.endlooplabel:
            raise ObinRuntimeError(W_String(u"Break outside loop"))
        if self.pop_after_break[-1] is True:
            self.emit('POP')
        self.emit('JUMP', self.endlooplabel[-1])

    def emit_continue(self):
        if not self.startlooplabel:
            raise ObinRuntimeError(W_String(u"Continue outside loop"))
        self.emit('JUMP', self.updatelooplabel[-1])

    def continue_at_label(self, label):
        self.updatelooplabel.append(label)

    def done_continue(self):
        self.updatelooplabel.pop()

    def is_compiled(self):
        return self.compiled_opcodes is not None

    def emit(self, operation, *args):
        from obin.utils import tb
        # if operation == "POP":
        #     tb()
        assert not self.compiled_opcodes
        opcode = getattr(opcodes, operation)(*args)
        self.opcodes.append(opcode)
        return opcode

    emit._annspecialcase_ = 'specialize:arg(1)'

    def emit_str(self, s):
        return self.emit('LOAD_STRINGCONSTANT', s)

    def emit_int(self, i):
        return self.emit('LOAD_INTCONSTANT', i)

    def unpop(self):
        from obin.runtime.opcodes import POP
        if self.opcodes and isinstance(self.opcodes[-1], POP):
            self.opcodes.pop()
            return True
        else:
            return False

    def returns(self):
        from obin.runtime.opcodes import RETURN
        if self.opcodes and isinstance(self.opcodes[-1], RETURN):
            return True
        return False

    def unlabel(self):
        if self.has_labels:
            self.remove_labels()

    def compile(self):
        assert not self.compiled_opcodes
        assert self._symbols
        self.unlabel()
        self.compiled_opcodes = [o for o in self.opcodes]
        self.estimated_stack_size()

    def remove_labels(self):
        """ Basic optimization to remove all labels and change
        jumps to addresses. Necessary to run code at all
        """
        if not self.has_labels:
            raise ObinRuntimeError("Already has labels")
        labels = {}
        counter = 0
        for i in range(len(self.opcodes)):
            op = self.opcodes[i]
            if isinstance(op, LABEL):
                labels[op.num] = counter
            else:
                counter += 1
        self.opcodes = [op for op in self.opcodes if not isinstance(op, LABEL)]
        for op in self.opcodes:
            if isinstance(op, BaseJump):
                op.where = labels[op.where]
        self.has_labels = False

    @jit.elidable
    def get_opcode(self, pc):
        assert pc >= 0
        return self.compiled_opcodes[pc]

    def length(self):
        return len(self.opcodes)

    @jit.elidable
    def opcode_count(self):
        return len(self.compiled_opcodes)

    def tostring(self):
        return str([repr(i) for i in self.opcodes])

    def __repr__(self):
        return "\n".join([repr(i) for i in self.opcodes])
