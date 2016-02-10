from obin.types import space, plist, environment
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


def _find_static_ref(ref1, ref2):
    # ref2 is tuple (ref, idx)
    return api.equal_b(ref1.name, api.at_index(ref2, 0).name)


class Scope:
    def __init__(self):
        self.locals = space.newmap()

        self.arg_count = -1
        self.fn_name_index = -1
        self.literals = ScopeSet()
        self.references = ScopeSet()
        self.static_references = plist.empty()
        self.is_variadic = None

    def has_possible_static_reference(self, ref):
        return plist.contains_with(self.static_references, ref, _find_static_ref)

    def add_possible_static_reference(self, ref):
        ref_idx = self.get_scope_reference(ref.name)
        assert not platform.is_absent_index(ref_idx), "Invalid static reference declaration. Reference id not defined"

        self.static_references = plist.prepend(space.newtuple([ref, space.newint(ref_idx)]), self.static_references)

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

    def declared_references(self):
        return self.references.values

    def declared_literals(self):
        return self.literals.values

    def _create_references(self, prev_scope):
        declared = self.declared_references()
        size = len(declared)
        if size == 0:
            return None

        refs = environment.newreferences_size(size)
        for static_record in self.static_references:
            static_ref = api.at_index(static_record, 0)
            static_ref_id = api.to_i(api.at_index(static_record, 1))

            prev_local_idx = prev_scope.get_scope_local_index(static_ref.name)
            # local in prev scope overrides static reference
            if not platform.is_absent_index(prev_local_idx):
                continue

            refs._set_refs(static_ref_id, static_ref)

        return refs

    def finalize(self, previous_scope):
        refs = self._create_references(previous_scope)

        return space.newscope(self.locals, refs, self.declared_references(),
                              self.declared_literals(),
                              self.arg_count, self.is_variadic, self.fn_name_index)
