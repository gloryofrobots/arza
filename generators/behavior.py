class Arg(object):
    def __init__(self, name):
        self.name = name
        self.type = "OAny"
    pass

class Method(object):
    def __init__(self, name, arity,  methodType=None, isGeneric=True, isMutator=False):
        self.name = name
        self.arity = arity
        if not methodType:
            self.type = 'ofunc_%d' % self.arity
        else:
            self.type = methodType
        
        self.args = [Arg("self")]
        for i in range(1, self.arity):
            self.args.append(Arg("arg%d" % i))

        self.isGeneric = isGeneric
        self.isMutator = isMutator
        name = self.name.replace("__", "")
        self.generic_name = "o%s" % name

    def as_dict(self):
        return self.__dict__

class Methods(object):
    def __init__(self, name, *methods):
        self.name = name
        self.methods = methods

    def __iter__(self):
        return self.methods.__iter__()

MEMORY = Methods("MEMORY", 
    Method('__destroy__', 1, "odestructor"),
    Method('__mark__', 1, "ofunc_each")
    )

BASE = Methods("BASE", 
    Method('__tostring__', 1),
    Method('__tobool__', 1),
    Method('__clone__', 1),
    Method('__compare__', 2),
    Method('__hash__', 1),
    Method('__equal__', 2, isGeneric=False),
    )

COLLECTION = Methods("COLLECTION", 
    Method('__iterator__', 1),
    Method('__length__', 1),
    Method('__getitem__', 2),
    Method('__hasitem__', 2),
    Method('__delitem__', 2, isMutator=True),
    Method('__setitem__', 3, isMutator=True),
    )

GENERATOR = Methods("GENERATOR", Method('__next__', 1))

NUMBER = Methods("NUMBER", 
    Method('__tointeger__', 1),
    Method('__tofloat__', 1),
    Method('__tonegative__', 1),
    Method('__invert__', 1),

    Method('__add__', 2),
    Method('__subtract__', 2),
    Method('__divide__', 2),
    Method('__multiply__', 2),
    Method('__leftshift__', 2),
    Method('__rightshift__', 2),
    Method('__mod__', 2),
    Method('__bitand__', 2),
    Method('__bitor__', 2),
    Method('__bitxor__', 2),
    )


BEHAVIOR = [
MEMORY,BASE, COLLECTION, GENERATOR, NUMBER,
]
