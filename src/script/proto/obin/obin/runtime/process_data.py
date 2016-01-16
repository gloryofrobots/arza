class Symbols:
    def __init__(self):
        self.symbols = []
        self.bindings = {}

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
    def __init__(self, path):
        assert isinstance(path, list)
        self.modules = {}
        self.path = path

    def add_path(self, path):
        assert isinstance(path, str)
        self.path.append(path)

    def add_module(self, name, module):
        self.modules[name] = module

    def get_module(self, name):
        return self.modules[name]


class ProcessData:
    def __init__(self, modules, std, builtins, symbols):
        self.modules = modules
        self.std_objects = std
        self.builtins = builtins
        self.symbols = symbols


def create(libdirs):
    from obin.types.space import newmap
    from obin.builtins.std import Std
    symbols = Symbols()
    stdlib = Std(symbols)
    builtins = newmap()
    modules = Modules(libdirs)
    return ProcessData(modules, stdlib, builtins, symbols)
