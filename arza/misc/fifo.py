
class Fifo:
    def __init__(self):
        self.first = ()

    def is_empty(self):
        v = self.first == ()
        return v

    def append(self, data):
        node = [data, ()]
        if self.first:
            self.last[1] = node
        else:
            self.first = node
        self.last = node

    def pop(self):
        node = self.first
        self.first = node[1]
        return node[0]
