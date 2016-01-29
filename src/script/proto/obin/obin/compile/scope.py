from obin.types import space
from obin.utils.misc import absent_index, is_absent_index
from obin.types import api


class ScopeSet:
    def __init__(self):
        self.values = []

    def get(self, val):
        try:
            return self.values.index(val)
        except ValueError:
            return absent_index()

    def add(self, val):
        assert val not in self.values
        self.values = self.values + [val]
        return len(self.values) - 1


class Scope:
    def __init__(self):
        self.locals = space.newmap()

        self.arg_count = -1
        self.fn_name_index = -1
        self.outers = []

        self.literals = ScopeSet()
        self.references = ScopeSet()
        self.is_variadic = None

    def get_reference(self, name):
        return self.references.get(name)

    def add_reference(self, name):
        assert space.issymbol(name)
        return self.references.add(name)

    def get_literal(self, literal):
        return self.literals.get(literal)

    def add_literal(self, literal):
        return self.literals.add(literal)

    def is_function_scope(self):
        return self.arg_count != -1

    def check_arg_count(self):
        assert self.arg_count != -1

    # RECURSIVE CALLS OPTIMISATION
    def add_function_name(self, name):
        self.fn_name_index = self.add_local(name)

    def declare_arguments(self, args_count, is_varargs):
        self.arg_count = args_count
        self.is_variadic = is_varargs

    def add_local(self, local):
        assert space.issymbol(local)
        self.check_arg_count()
        assert is_absent_index(self.get_local_index(local))
        return self.locals.insert(local, space.newnil())

    def get_local_index(self, local):
        return api.get_index(self.locals, local)

    def add_outer(self, name):
        assert space.issymbol(name)
        assert name not in self.outers
        self.outers.append(name)

    def has_outer(self, name):
        assert space.issymbol(name)
        return name in self.outers

    def finalize(self):
        return FinalScope(self.locals, self.references.values,
                          self.literals.values,
                          self.arg_count, self.is_variadic, self.fn_name_index)


class FinalScope:
    # _immutable_fields_ = ['vars', 'arg_count', 'fn_name_index',
    #                       'references[*]', 'is_varargs', 'count_refs', 'count_vars', 'literals', 'functions']

    def __init__(self, variables, references, literals, arg_count, is_varargs, fn_name_index):
        self.variables = variables
        self.count_args = arg_count
        self.fn_name_index = fn_name_index
        self.references = references
        self.literals = literals
        self.is_variadic = is_varargs
        self.count_refs = len(self.references)
        self.count_vars = api.n_length(self.variables)

    def create_env_bindings(self):
        return api.clone(self.variables)
