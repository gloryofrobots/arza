from obin.objects.object_map import new_map
from object_space import isstring

class SymbolMap(object):
    def __init__(self):
        self.symbols = new_map()
        self.functions = []
        self.variables = []
        self.parameters = []
        self.rest = None

    def __eq__(self, other):
        return self.functions == other.functions \
               and self.variables == other.variables \
               and self.parameters == other.parameters \
                and self.symbols == other.symbols

    def add_symbol(self, identifyer):
        assert isstring(identifyer)
        idx = self.symbols.lookup(identifyer)

        if idx == self.symbols.NOT_FOUND:
            self.symbols = self.symbols.add(identifyer)
            idx = self.symbols.lookup(identifyer)

        assert isinstance(idx, int)
        return idx

    def has_variable(self, identifyer):
        assert isstring(identifyer)
        return identifyer in self.variables

    def add_variable(self, identifyer):
        idx = self.add_symbol(identifyer)
        self.variables.append(identifyer)
        return idx

    def add_function(self, identifyer):
        idx = self.add_symbol(identifyer)

        self.functions.append(identifyer)
        return idx

    def add_rest(self, identifyer):
        self.rest = identifyer
        idx = self.add_symbol(identifyer)
        return idx

    def add_parameter(self, identifyer):
        idx = self.add_symbol(identifyer)
        self.parameters.append(identifyer)
        return idx

    def get_index(self, identifyer):
        assert isstring(identifyer)
        return self.symbols.lookup(identifyer)

    def get_symbols(self):
        return self.symbols.keys()

    def len(self):
        return self.symbols.len()

    def finalize(self):
        return FinalSymbolMap(self.symbols, self.functions, self.variables, self.parameters, self.rest)


class FinalSymbolMap(object):
    _immutable_fields_ = ['symbols', 'functions[*]', 'variables[*]', 'parameters[*]']

    def __init__(self, symbols, functions, variables, parameters, rest):
        self.symbols = symbols
        self.functions = functions[:]
        self.variables = variables[:]
        self.parameters = parameters[:]
        self.rest = rest

    def get_index(self, identifyer):
        return self.symbols.lookup(identifyer)

    def get_symbols(self):
        return self.symbols.keys()

    def len(self):
        return self.symbols.len()
