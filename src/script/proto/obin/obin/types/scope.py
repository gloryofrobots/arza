from obin.types import api
from obin.types.root import W_Any


class W_Scope(W_Any):
    # _immutable_fields_ = ['vars', 'arg_count', 'fn_name_index',
    #                       'references[*]', 'is_varargs', 'count_refs', 'count_vars', 'literals', 'functions']

    def __init__(self, variables, references, reference_names, literals, operators, imports, arg_count, is_varargs,
                 fn_name_index):
        self.variables = variables
        self.count_args = arg_count
        self.fn_name_index = fn_name_index
        self.references = references
        self.reference_names = reference_names
        self.literals = literals
        self.imports = imports
        self.is_variadic = is_varargs
        self.operators = operators

    def create_references(self):
        if self.references is None:
            return None
        return api.clone(self.references)

    def create_operators(self):
        if self.operators is None:
            return None
        return api.clone(self.operators)

    def create_env_bindings(self):
        return api.clone(self.variables)
