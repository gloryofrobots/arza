from arza.types import space, api, plist
from arza.compile.parse.parser import newparser
from arza.runtime import error
from arza.types import api

class Symbols:
    def __init__(self):
        self.symbols = []
        self.bindings = {}

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
            from arza.types.space import newstring
            from arza.types.symbol import W_Symbol
            string = newstring(ustrval)
            idx = len(self.symbols)
            symbol = W_Symbol(string, idx)
            self.symbols.append(symbol)
            self.bindings[ustrval] = idx
            return symbol

    def get(self, idx):
        return self.symbols[idx]


class Modules:
    def __init__(self, path, prelude):
        error.affirm_type(path, space.islist)
        error.affirm_iterable(path, space.isstring)

        self.modules = space.newassocarray()
        self.path = path
        self.prelude = prelude

    def add_path(self, path):
        error.affirm_type(path, space.isstring)
        self.path = plist.cons(path, self.path)

    def add_module(self, module):
        error.affirm_type(module.name, space.issymbol)
        error.affirm_type(module, space.isenv)
        api.put(self.modules, module.name, module)

    def before_load(self, name):
        error.affirm_type(name, space.issymbol)

        assert not api.contains_b(self.modules, name)
        api.put(self.modules, name, space.newint(0))

    def has_module(self, name):
        error.affirm_type(name, space.issymbol)
        return api.contains_b(self.modules, name)

    def get_module(self, name):
        error.affirm_type(name, space.issymbol)
        m = api.at(self.modules, name)
        if space.isint(m):
            error.throw_2(error.Errors.IMPORT_ERROR, u"Cross reference import", name)
        return m

    def set_prelude(self, prelude):
        self.prelude = prelude


class ProcessData:
    def __init__(self, scheduler, modules, std, symbols, io):
        self.scheduler = scheduler
        self.modules = modules
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
    from arza.builtins.std import Std
    symbols = Symbols()
    stdlib = Std(symbols)
    modules = Modules(libdirs, prelude)
    io = IO()
    return ProcessData(scheduler, modules, stdlib, symbols, io)
