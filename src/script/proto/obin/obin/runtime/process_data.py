class Symbols:
    def __init__(self):
        self.symbols = []
        self.bindings = {}

    def add_symbol(self, ustrval):
        assert isinstance(ustrval, unicode)
        try:
            idx = self.bindings[ustrval]
            symbol = self.symbols[idx]
            return symbol
        except KeyError:
            from obin.objects.space import newstring, newsymbol
            string = newstring(ustrval)
            idx = len(self.symbols)
            symbol = newsymbol(string, idx)
            self.symbols.append(symbol)
            self.symbols[ustrval] = idx
            return symbol

    def get_symbol(self, idx):
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


def create(libdirs, stdlib, builtins):
    modules = Modules(libdirs)
    symbols = Symbols()
    return ProcessData(modules, stdlib, builtins, symbols)
