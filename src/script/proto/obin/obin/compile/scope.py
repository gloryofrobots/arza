from obin.objects.object_space import isstring
from obin.objects.slots import newslots_empty, newslots_with_values_from_slots

class Scope(object):
    def __init__(self):
        self.locals = newslots_empty()

        self.arg_count = -1
        self.fn_name_index = -1
        self.outers = []

        self.arguments = []
        self.references = []
        self.is_variadic = False

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
        assert self.get_local_index(local) is None
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

    def get_reference(self, name):
        assert isstring(name)
        try:
            return self.references.index(name)
        except ValueError:
            return None

    def add_reference(self, ref):
        assert isstring(ref)
        assert ref not in self.references
        self.references.append(ref)
        return len(self.references) - 1

    def finalize(self):
        return FinalScope(self.locals, self.arguments, self.references,  self.arg_count, self.is_variadic, self.fn_name_index)


class FinalScope(object):
    _immutable_fields_ = ['vars', 'arg_count', 'fn_name_index',
                          'references[*]', 'is_varargs', 'count_refs', 'count_vars']

    def __init__(self, variables, arguments, references, arg_count, is_varargs, fn_name_index):
        self.variables = variables
        self.count_args = arg_count
        self.fn_name_index = fn_name_index
        self.references = references
        self.is_variadic = is_varargs
        self.count_refs = len(self.references)
        self.count_vars = self.variables.length()
        self.arguments = arguments

    def create_object(self):
        from copy import copy
        from obin.objects.object_space import newplainobject_with_slots
        return newplainobject_with_slots(copy(self.variables))

    def create_environment_slots(self, arguments):
        return newslots_with_values_from_slots(arguments, self.variables)
