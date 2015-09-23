from kermit.kermit.obin.helpers import *
from kermit.kermit.obin.cell import *
from kermit.kermit.obin.stack import *

class Executable(Cell):
    def __init__(self):
        super(Executable, self).__init__()

    def createRoutine(self):
        pass

class BytecodeRoutine(Cell):
    def __init__(self, executable):
        super(BytecodeRoutine, self).__init__()
        self.executable = executable


class BytecodeFunction(Executable):
    def __init__(self):
        super(BytecodeFunction, self).__init__()
        self.bytecode = Bytecode()
        self.literals = []
        self.argumentNames = []




class State(object):
    pass


class Machine(object):
    def __init__(self):

        pass

def main():
    pass

main()