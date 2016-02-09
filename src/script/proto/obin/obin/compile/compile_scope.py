from obin.types import space
from obin.misc import platform
from obin.types import api


class ScopeSet:
    def __init__(self):
        self.values = []

    def get(self, val):
        try:
            return self.values.index(val)
        except ValueError:
            return platform.absent_index()

    def add(self, val):
        assert val not in self.values
        self.values = self.values + [val]
        return len(self.values) - 1


class Scope:
    def __init__(self):
        self.locals = space.newmap()

        self.arg_count = -1
        self.fn_name_index = -1
        self.literals = ScopeSet()
        self.references = ScopeSet()
        self.is_variadic = None

    def get_scope_reference(self, name):
        return self.references.get(name)

    def add_scope_reference(self, name):
        assert space.issymbol(name)
        return self.references.add(name)

    def get_scope_literal(self, literal):
        return self.literals.get(literal)

    def add_scope_literal(self, literal):
        return self.literals.add(literal)

    def check_arg_count(self):
        assert self.arg_count != -1

    # RECURSIVE CALLS OPTIMISATION
    def add_scope_function_name(self, name):
        self.fn_name_index = self.add_scope_local(name)

    def declare_scope_arguments(self, args_count, is_varargs):
        self.arg_count = args_count
        self.is_variadic = is_varargs

    def add_scope_local(self, local):
        assert space.issymbol(local)
        self.check_arg_count()
        assert platform.is_absent_index(self.get_scope_local_index(local))
        return self.locals.insert(local, space.newnil())

    def get_scope_local_index(self, local):
        return api.get_index(self.locals, local)

    def finalize(self):
        return space.newscope(self.locals, self.references.values,
                              self.literals.values,
                              self.arg_count, self.is_variadic, self.fn_name_index)
