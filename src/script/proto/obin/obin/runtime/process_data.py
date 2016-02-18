from obin.types import space
from obin.compile.parse.parser import newparser
from obin.runtime import error

class Symbols:
    def __init__(self):
        self.symbols = []
        self.bindings = {}

    def symbol_s(self, strval):
        return self.symbol(unicode(strval))

    def symbol(self, ustrval):
        assert isinstance(ustrval, unicode)
        try:
            idx = self.bindings[ustrval]
            symbol = self.symbols[idx]
            return symbol
        except KeyError:
            from obin.types.space import newstring
            from obin.types.symbol import W_Symbol
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
        assert isinstance(path, list)
        self.modules = {}
        self.path = path
        self.prelude = prelude

    def add_path(self, path):
        assert isinstance(path, str)
        self.path.append(path)

    def add_module(self, name, module):
        self.modules[name] = module

    def before_load(self, name):
        assert name not in self.modules
        self.modules[name] = None

    def get_module(self, name):
        m = self.modules[name]
        if m is None:
            raise RuntimeError("Load cycle")
        return m

    def set_prelude(self, prelude):
        self.prelude = prelude


class ProcessData:
    def __init__(self, modules, std, symbols, io):
        self.modules = modules
        self.std = std
        self.symbols = symbols
        self.io = io
        self.parser = newparser(self)


class IO:
    def __init__(self):
        from obin.types.iodevice import IoDevice
        import sys
        self.stdout = IoDevice(sys.stdout)
        self.stderr = IoDevice(sys.stderr)
        self.stdin = IoDevice(sys.stdin)


def create(libdirs, prelude):
    from obin.builtins.std import Std
    symbols = Symbols()
    stdlib = Std(symbols)
    modules = Modules(libdirs, prelude)
    io = IO()
    return ProcessData(modules, stdlib, symbols, io)
