__author__ = 'gloryofrobots'

class Bytecode(object):
    def __init__(self):
        self.data = []

    def push(self, operation):
        self.data.append(operation)


class Stack(object):
    def __init__(self):
        self.data = []

    def push(self, value):
        self.data.append(value)

    def rewind(self, index):
        del self.data[index:]

    def top(self):
        return self.data[len(self.data) - 1]

    def pop(self):
        return self.data.pop()
