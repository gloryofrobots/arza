from arza.types import api, space, plist
from arza.runtime import error


def find_in_module(process, prelude, name):
    sym = space.newsymbol(process, name)
    if not api.contains(prelude, sym):
        error.throw_1(error.Errors.KEY_ERROR, space.newstring(u"Missing internal trait %s in prelude" % name))
    return api.at(prelude, sym)


def newclass(name, baseclass):
    from arza.types.space import newemptyclass
    return newemptyclass(name, baseclass)


class StdClasses:
    def __init__(self, symbols):
        _s = symbols.symbol
        self.Object = newclass(_s(u"Object"), space.newnil())
        self.Class = newclass(_s(u"Class"), self.Object)
        self.Object.retype(self.Class)

        newtype = lambda name: newclass(name, self.Object)
        newtype_2 = lambda name, parent: newclass(name, parent)

        self.Bool = newtype(_s(u"Bool"))

        self.Char = newtype(_s(u"Char"))

        self.Number = newtype(_s(u"Number"))

        self.Int = newtype_2(_s(u"Int"), self.Number)

        self.Float = newtype_2(_s(u"Float"), self.Number)

        self.Symbol = newtype(_s(u"Symbol"))

        self.String = newtype(_s(u"String"))

        self.List = newtype(_s(u"List"))

        self.Array = newtype(_s(u"Array"))

        self.Vector = newtype(_s(u"Vector"))

        self.Tuple = newtype(_s(u"Tuple"))

        self.Dict = newtype(_s(u"Dict"))

        self.Function = newtype(_s(u"Function"))

        self.FiberChannel = newtype(_s(u"FiberChannel"))

        self.File = newtype(_s(u"File"))

        self.IO = newtype(_s(u"IO"))

        self.Coroutine = newtype(_s(u"Coroutine"))

        self.Env = newtype(_s(u"Env"))

        self.PID = newtype(_s(u"PID"))


class Functions:
    def __init__(self):
        self.new = None

    def setup(self, process):
        prelude = process.classes.prelude
        self.new = self.find_function(process, prelude, u"__new__")

    def find_function(self, process, module, name):
        _fun = find_in_module(process, module, name)
        error.affirm_type(_fun, space.isfunction)
        return _fun


class Std:
    def __init__(self, symbols):
        # self.functions = Functions()
        self.classes = StdClasses(symbols)
        self.initialized = False

    def postsetup(self, process):
        # self.functions.setup(process)
        self.initialized = True
