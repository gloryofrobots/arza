from rpython.rlib import jit
from obin.compile.code import *


def estimate_stack_size(opcodes):
    max_size = 0
    moving_size = 0
    for opcode in opcodes:
        moving_size += opcode_estimate_stack_change(opcode)
        max_size = max(moving_size, max_size)
    assert max_size >= 0
    return max_size


class CodeSource:
    _immutable_fields_ = ['compiled_opcodes[*]', 'scope']

    """ That object stands for code of a single javascript function
    """

    def __init__(self):
        self.opcodes = []
        self.label_count = 0
        self.startlooplabel = []
        self.endlooplabel = []
        self.pop_after_break = []
        self.updatelooplabel = []
        self.estimated_stack_size = -1
        self.scope = None
        self._function_name_ = None
        # VALUE FOR AUTOMATIC RETURN
        self.emit_0(UNDEFINED)

    def finalize_compilation(self, scope_info):
        assert scope_info
        self.scope = scope_info
        self.emit_0(RETURN)
        self.__remove_labels()
        self.estimated_stack_size = estimate_stack_size(self.opcodes)
        return Code(self.opcodes, self.estimated_stack_size, self.scope)

    def prealocate_label(self):
        num = self.label_count
        self.label_count += 1
        return num

    def prealocate_endloop_label(self, pop=False):
        num = self.prealocate_label()
        self.endlooplabel.append(num)
        self.pop_after_break.append(pop)
        return num

    def prealocate_updateloop_label(self):
        num = self.prealocate_label()
        self.updatelooplabel.append(num)
        return num

    def emit_2(self, opcode, arg1, arg2):
        assert isinstance(opcode, int)
        assert isinstance(arg1, int)
        assert isinstance(arg2, int)
        # from obin.utils import tb
        # if operation == "LOAD_UNDEFINED":
        #     tb(args)
        self.opcodes.append((opcode, arg1, arg2))
        return opcode

    def emit_0(self, operation):
        self.emit_2(operation, 0, 0)

    def emit_1(self, operation, arg1):
        self.emit_2(operation, arg1, 0)

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
            return False
        if self.pop_after_break[-1] is True:
            self.emit_0(POP)
        self.emit_1(JUMP, self.endlooplabel[-1])
        return True

    def emit_continue(self):
        if not self.startlooplabel:
            return False
        self.emit_1(JUMP, self.updatelooplabel[-1])
        return True

    def emit_label(self, num=-1):
        if num == -1:
            num = self.prealocate_label()
        self.emit_1(LABEL, num)
        return num

    def emit_startloop_label(self):
        num = self.emit_label()
        self.startlooplabel.append(num)
        return num

    def continue_at_label(self, label):
        self.updatelooplabel.append(label)

    def done_continue(self):
        self.updatelooplabel.pop()

    def __remove_labels(self):
        """ Basic optimization to remove all labels and change
        jumps to addresses. Necessary to run code at all
        """
        labels = {}
        counter = 0
        length = len(self.opcodes)
        for op in self.opcodes:
            tag = op[0]
            if is_label_opcode(tag):
                labels[op[1]] = counter
            else:
                counter += 1

        oldopcodes = self.opcodes
        new_length = length - len(labels)
        self.opcodes = [(0,0,0)] * new_length
        i = 0
        for op in oldopcodes:
            tag = op[0]
            if is_label_opcode(tag):
                continue
            else:
                if is_jump_opcode(tag):
                    # print "Jump %d => %d" % (op[1], labels[op[1]])
                    self.opcodes[i] = (tag, labels[op[1]], op[2])
                else:
                    self.opcodes[i] = op
                i += 1

    def length(self):
        return len(self.opcodes)

    def __repr__(self):
        return "\n".join([repr(i) for i in self.opcodes])


class Code:
    def __init__(self, opcodes, estimated_stack_size, scope):
        self.opcodes = opcodes
        self.estimated_stack_size = estimated_stack_size
        self.scope = scope

    @jit.elidable
    def get_opcode(self, pc):
        assert pc >= 0
        return self.opcodes[pc]

    @jit.elidable
    def length(self):
        return len(self.opcodes)

    def tostring(self):
        return str([(opcode_to_str(op[0]), op[1], op[2]) for op in self.opcodes])

    def __repr__(self):
        return "\n".join([str((opcode_to_str(op[0]), op[1], op[2])) for op in self.opcodes])
