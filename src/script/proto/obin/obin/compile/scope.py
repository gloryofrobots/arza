from obin.objects.object_space import isstring
from obin.objects.datastructs import Slots

class Scope(object):
    def __init__(self):
        self.locals = Slots()
        self.arg_count = -1
        self.fn_name_index = -1
        self.outers = []
        
        self.references = []
        self.is_varargs = False

    def is_function_scope(self):
        return self.arg_count == -1

    def check_arg_count(self):
        assert self.arg_count != -1

    # RECURSIVE CALLS OPTIMISATION
    def add_function_name(self, name):
        self.fn_name_index = self.add_local(name)

    def add_arguments(self, args, is_varargs):
        if args is None:
            self.arg_count = 0
            self.is_varargs = False
            return

        for arg in args:
            self.add_local(arg)

        self.is_varargs = is_varargs
        self.arg_count = len(args)

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
        return FinalScope(self.locals, self.references,  self.arg_count, self.is_varargs, self.fn_name_index)


class FinalScope(object):
    _immutable_fields_ = ['vars', 'arg_count', 'fn_name_index',
                          'references[*]', 'is_varargs', 'count_refs', 'count_vars']

    def __init__(self, variables, references, arg_count, is_varargs, fn_name_index):
        self.variables = variables
        self.arg_count = arg_count
        self.fn_name_index = fn_name_index
        self.references = references
        self.is_varargs = is_varargs
        self.count_refs = len(self.references)
        self.count_vars = self.variables.length()

    def create_object(self):
        from object_space import newplainobject_with_slots
        return newplainobject_with_slots(self.variables.clone())
