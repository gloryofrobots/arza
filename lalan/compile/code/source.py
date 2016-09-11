from lalan.misc.platform import jit
from lalan.compile.code.opcode import *
from lalan.misc.strutil import get_line


def estimate_stack_size(opcodes):
    max_size = 0
    moving_size = 0
    for opcode in opcodes:
        moving_size += opcode_estimate_stack_change(opcode)
        max_size = max(moving_size, max_size)
    assert max_size >= 0
    return max_size


class SourceInfo:
    def __init__(self, path, src):
        self.path = path
        self.src = src
        self.map = []

    def get_line(self, line_no):
        if self.src is None:
            return u""

        return get_line(self.src, line_no)

    def length(self):
        return len(self.map)

def codeinfo(pos, line, col):
    return pos, line, col


def codeinfo_unknown():
    return codeinfo(-1, -1, -1)


class CodeSource:
    # _immutable_fields_ = ['compiled_opcodes[*]', 'scope']

    def __init__(self, info):
        self.info = info
        self.opcodes = []
        self.label_count = 0
        self.estimated_stack_size = -1
        self.scope = None

    def finalize_compilation(self, scope_info):
        assert scope_info
        self.scope = scope_info
        self.emit_0(RETURN, codeinfo_unknown())
        self.__remove_labels()
        self.estimated_stack_size = estimate_stack_size(self.opcodes)
        return Code(self.opcodes, self.estimated_stack_size, self.scope, self.info)

    def prealocate_label(self):
        num = self.label_count
        self.label_count += 1
        return num

    def remove_last(self):
        self.opcodes.pop()
        self.info.map.pop()

    def last(self):
        return self.opcodes[-1]

    def emit_2(self, opcode, arg1, arg2, info):
        # from lalan.compile.code.utils import opcode_to_str
        assert isinstance(opcode, int)
        assert isinstance(arg1, int)
        assert isinstance(arg2, int)
        # print opcode_to_str(opcode), arg1, arg2
        self.info.map.append(info)
        self.opcodes.append((opcode, arg1, arg2))
        return opcode

    def emit_0(self, operation, info):
        # if operation == VOID:
        #     print "VOID"
        self.emit_2(operation, 0, 0, info)

    def emit_1(self, operation, arg1, info):
        self.emit_2(operation, arg1, 0, info)

    def emit_label(self, num=-1):
        if num == -1:
            num = self.prealocate_label()
        self.emit_1(LABEL, num, codeinfo_unknown())
        return num

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
        oldsource_map = self.info.map

        new_length = length - len(labels)
        self.opcodes = [(0, 0, 0)] * new_length
        self.info.map = [(0, 0, 0)] * new_length

        i = 0
        for j in range(len(oldopcodes)):
            op = oldopcodes[j]
            info = oldsource_map[j]

            tag = op[0]
            if is_label_opcode(tag):
                continue
            else:
                self.info.map[i] = info
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
    def __init__(self, opcodes, estimated_stack_size, scope, info):
        self.opcodes = opcodes
        self.estimated_stack_size = estimated_stack_size
        self.scope = scope
        self.info = info

    @jit.elidable
    def get_opcode(self, pc):
        assert pc >= 0
        return self.opcodes[pc]

    @jit.elidable
    def get_opcode_info(self, pc):
        if pc <= 0 or pc >= self.info.length():
            return None
        info = self.info.map[pc]
        if info[0] == -1:
            return self.get_opcode_info(pc - 1)
        return info

    @jit.elidable
    def length(self):
        return len(self.opcodes)

    def tostring(self):
        return str([(opcode_to_str(op[0]), op[1], op[2]) for op in self.opcodes])

    def __repr__(self):
        return "\n".join([str((opcode_to_str(op[0]), op[1], op[2])) for op in self.opcodes])
