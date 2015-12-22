from obin.objects.space import isstring
from obin.objects.slots import newslots_empty, newslots_with_values_from_slots

class ScopeSet:
    def __init__(self):
        self.values = []

    def get(self, val):
        try:
            return self.values.index(val)
        except ValueError:
            return -1000

    def add(self, val):
        assert val not in self.values
        self.values = self.values + [val]
        return len(self.values) - 1


class Scope:
    def __init__(self):
        self.locals = newslots_empty()

        self.arg_count = -1
        self.fn_name_index = -1
        self.outers = []
        self.arguments = []

        self.literals = ScopeSet()
        self.references = ScopeSet()
        self.is_variadic = False

    def get_reference(self, name):
        return self.references.get(name)

    def add_reference(self, name):
        assert isstring(name)
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

    def add_arguments(self, args, is_varargs):
        if args is None:
            self.arg_count = 0
            self.is_variadic = False
            return

        assert isinstance(args, list)
        self.arg_count = len(args)
        self.arguments = args
        for arg in args:
            self.add_local(arg)

        self.is_variadic = is_varargs

    def add_local(self, local):
        assert isstring(local)
        self.check_arg_count()
        assert self.get_local_index(local) is -1000
        return self.locals.add(local, None)

    def get_local_index(self, local):
        return self.locals.get_index(local)

    def add_outer(self, name):
        assert isstring(name)
        assert name not in self.outers
        self.outers.append(name)

    def has_outer(self, name):
        assert isstring(name)
        return name in self.outers

    def finalize(self):
        return FinalScope(self.locals, self.arguments, self.references.values,
                          self.literals.values,
                          self.arg_count, self.is_variadic, self.fn_name_index)


class FinalScope:
    _immutable_fields_ = ['vars', 'arg_count', 'fn_name_index',
                          'references[*]', 'is_varargs', 'count_refs', 'count_vars', 'literals', 'functions']

    def __init__(self, variables, arguments, references, literals, arg_count, is_varargs, fn_name_index):
        self.variables = variables
        self.count_args = arg_count
        self.fn_name_index = fn_name_index
        self.references = references
        self.literals = literals
        self.is_variadic = is_varargs
        self.count_refs = len(self.references)
        self.count_vars = self.variables.length()
        self.arguments = arguments

    def create_object(self):
        from obin.objects.space import newplainobject_with_slots
        return newplainobject_with_slots(self.variables.copy())

    def create_environment_slots(self, arguments):
        return newslots_with_values_from_slots(arguments, self.variables)
