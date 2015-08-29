__author__ = 'gloryofrobots'
from helpers import List
from copy import deepcopy

class __Nothing:
    pass

Nothing = __Nothing()

class Table(object):
    def __init__(self):
        self.data = {}

    def get(self, item):
        return self.data.get(item, Nothing)

    def set(self, key, value):
        self.data[key] = value

    def __repr__(self):
        return str(self.data)

class Cell(object):
    def __init__(self):
        self.meta = [Table()]
        self.name = "Cell"

    def __repr__(self):
        return self.name + ": " + str(self.meta)

    def get(self, item):
        for trait in self.meta:
            value = trait.get(item)
            if value is not Nothing:
                return value

        return Nothing

    @property
    def scope(self):
        return self.meta[0]

    def set(self, key, value):
        self.scope.set(key, value)

    def isa(self, cell):
        self.meta.append(cell)

    def nota(self, cell):
        self.meta.remove(cell)

    def kindof(self, cell):
        if cell is self:
            return True
        for trait in self.meta[1:]:
            if trait.kindof(cell):
                return True
        return False

class Origin(Cell):
    def __call__(self, name, *args, **kwargs):
        cell = Origin(*args, **kwargs)
        cell.isa(self)
        cell.name = name
        return cell

class Env(Cell):
    def __init__(self):
        super(Env, self).__init__()
        self.next = None

    def link(self, scope):
        self.next = scope

    def get(self, name):
        scope = self
        while scope:
            item = scope.get(name)
            if item is not Nothing:
                return item
            scope = scope.next

Something = Origin()
Human = Something("Human")
Boring = Something("Boring")
Boris = Human("Boris")
Boris.isa(Boring)

print Boris.kindof(Human)
print Boris.kindof(Boring)
print Boris.kindof(Something)
print Boris
Boris.nota(Boring)
print Boris.kindof(Boring)
print Boris



