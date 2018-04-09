from capy.types import space, api, plist
from capy.compile.parse.parser import newparser
from capy.runtime import error
from capy.types import api


class Symbols:
    def __init__(self):
        self.symbols = []
        self.bindings = {}
        self.init = self.symbol(u"__init__")
        self.dot = self.symbol(u".")

    def symbol_s(self, strval):
        return self.symbol(unicode(strval))

    def symbol_string(self, string):
        return self.symbol(api.to_u(string))

    def symbol(self, ustrval):
        assert isinstance(ustrval, unicode)
        try:
            idx = self.bindings[ustrval]
            symbol = self.symbols[idx]
            return symbol
        except KeyError:
            from capy.types.space import newstring
            from capy.types.symbol import W_Symbol
            string = newstring(ustrval)
            idx = len(self.symbols)
            symbol = W_Symbol(string, idx)
            self.symbols.append(symbol)
            self.bindings[ustrval] = idx
            return symbol

    def get(self, idx):
        return self.symbols[idx]


class Classes:
    def __init__(self, path, prelude):
        error.affirm_type(path, space.islist)
        error.affirm_iterable(path, space.isstring)

        self.classes = space.newemptytable()
        self.path = path
        self.prelude = prelude

    def add_path(self, path):
        error.affirm_type(path, space.isstring)
        self.path = plist.cons(path, self.path)

    def add_env(self, base, env):
        module = space.newcompiledclass(space.newnil(), base, env)
        self.add_class(module)
        return module

    def add_class(self, _class):
        error.affirm_type(_class.name, space.issymbol)
        error.affirm_type(_class, space.isclass)
        api.put(self.classes, _class.name, _class)

    def before_load(self, name):
        error.affirm_type(name, space.issymbol)

        assert not api.contains_b(self.classes, name)
        api.put(self.classes, name, space.newint(0))

    def has_module(self, name):
        error.affirm_type(name, space.issymbol)
        return api.contains_b(self.classes, name)

    def get_class(self, name):
        error.affirm_type(name, space.issymbol)
        m = api.at(self.classes, name)
        if space.isint(m):
            error.throw_2(error.Errors.IMPORT_ERROR, u"Cross reference import", name)
        return m

    def set_prelude(self, prelude):
        self.prelude = prelude


class ProcessData:
    def __init__(self, scheduler, modules, std, symbols, io):
        self.scheduler = scheduler
        self.classes = modules
        self.std = std
        self.symbols = symbols
        self.io = io
        self.parser = newparser()


class IO:
    def __init__(self):
        import sys
        self.stdout = space.newiodevice(sys.stdout)
        self.stderr = space.newiodevice(sys.stderr)
        self.stdin = space.newiodevice(sys.stdin)


def create(scheduler, libdirs, prelude):
    from capy.builtins.std import Std
    symbols = Symbols()
    stdlib = Std(symbols)
    classes = Classes(libdirs, prelude)
    io = IO()
    return ProcessData(scheduler, classes, stdlib, symbols, io)
