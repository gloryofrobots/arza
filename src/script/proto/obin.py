from zmq.tests.test_socket import S
from helpers import List

class Context(object):
    pass

class Environment(object):
    def __init__(self):
        pass

class Scope(object):
    def __init__(self):
        self.data = []
        self.bindings = {}

    def set(self, name, value):
        self.data.append(value)
        self.bindings[name] = len(self.data) - 1

    def atName(self, name):
        return self.data[self.bindings[name]]

    def atIndex(self, index):
        return self.data[index]

class Cell(object):
    def __init__(self):
        self.scopes = List()
        scope = Scope()
        self.scopes.append(scope)
        traits = List()
        self.scopes.append(traits)

    def scope(self):
        return self.scopes.first()

    def traits(self):
        return self.scopes.second()

    def frames(self):
        return self.scopes.third()

    def enter(self, scopes):
        self.scopes.append(scopes)

    def isa(self, cell):
        self.frames().append(cell.scopes)


class Scope(object):
    def __init__(self):
        self.data = []
        self.bindings = {}

    def set(self, name, value):
        self.data.append(value)
        self.bindings[name] = len(self.data) - 1

    def atName(self, name):
        return self.data[self.bindings[name]]

    def atIndex(self, index):
        return self.data[index]


class Cell2(Scope):
    def __init__(self):
        super(Scope, self).__init__()
        self.context = None
        self.traits = List()

    def lookup(self, name):
        pass


    def scope(self):
        return self.scopes.first()

    def traits(self):
        return self.scopes.second()

    def frames(self):
        return self.scopes.third()

    def enter(self, scopes):
        self.scopes.append(scopes)

    def isa(self, cell):
        self.frames().append(cell.scopes)

class Executable(object):
    def __
    pass


class State(object):
    pass


class Machine(object):
    def __init__(self):

        pass

def main():
    pass

main()