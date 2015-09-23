__author__ = 'gloryofrobots'
class OAny(object):
    pass

class OType(OAny):
    def __init__(self, atom):
        self.atom = atom

class OInt(OAny):
    def __init__(self, value):
        assert(isinstance(value, int))
        self.value = value

class OFloat(OAny):
    def __init__(self, value):
        assert(isinstance(value, float))
        self.value = value

ONothing = OAny()
ONil = OAny()
OTrue = OAny()
OFalse = OAny()

class OTable(OAny):
    def __init__(self, data=None):
        if not data:
            self.data = {}
        else:
            assert(isinstance(data, dict))
            self.data = data

    def get(self, item):
        return self.data.get(item, ONothing)

    def set(self, key, value):
        self.data[key] = value

    def __repr__(self):
        return str(self.data)

class OVector(OAny):
    def __init__(self, data=None):
        if not data:
            self.data = {}
        else:
            assert(isinstance(data, dict))
            self.data = data


class Object(OAny):
    def __init__(self):
        self.forms = [OTable()]
        self.name = "Object"

    def __repr__(self):
        return self.name + ": " + str(self.forms)

    def get(self, item):
        for trait in self.forms:
            value = trait.get(item)
            if value is not ONothing:
                return value

        return ONothing

    @property
    def scope(self):
        return self.forms[0]

    def set(self, key, value):
        self.scope.set(key, value)

    def isa(self, cell):
        self.forms.append(cell)

    def nota(self, cell):
        self.forms.remove(cell)

    def kindof(self, cell):
        if cell is self:
            return True
        for trait in self.forms[1:]:
            if trait.kindof(cell):
                return True
        return False


def form(S, cell, typename, *args, **kwargs):


class Env(Object):
    def __init__(self):
        super(Env, self).__init__()
        self.next = None

    def link(self, scope):
        self.next = scope

    def get(self, name):
        scope = self
        while scope:
            item = scope.get(name)
            if item is not ONothing:
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


