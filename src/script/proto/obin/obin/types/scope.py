from obin.types import api
from obin.types.root import W_Any


class W_Scope(W_Any):
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
