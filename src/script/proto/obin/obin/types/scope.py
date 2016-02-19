from obin.types import space, plist, environment
from obin.types.root import W_Any
from obin.misc import platform
from obin.types import api


class ScopeSet:
    def __init__(self):
        # TODO USE PLIST
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


def _find_function(symbol, record):
    return api.equal_b(symbol, api.at_index(record, 0))


class W_Scope(W_Any):
    def __init__(self):
        self.__locals = space.newmap()

        self.arg_count = -1
        self.__literals = ScopeSet()
        self.__local_references = ScopeSet()
        self.__operators = space.newmap()
        self.imports = space.newmap()
        self.exports = plist.empty()
        self.functions = space.newmap()
        self.__static_references = plist.empty()
        self.__references = None
        self.is_variadic = None

    ######################################################
    def add_export(self, name):
        assert space.issymbol(name)
        assert not self.has_export(name)
        self.exports = plist.cons(name, self.exports)

    def has_export(self, name):
        assert space.issymbol(name)
        return plist.contains(self.exports, name)

    def add_imported(self, name, func):
        assert space.issymbol(name)
        assert platform.is_absent_index(self.get_imported_index(name))
        return self.imports.insert(name, func)

    def get_imported_index(self, name):
        return api.get_index(self.imports, name)

    def add_function(self, symbol, idx):
        self.functions.insert(symbol, space.newint(idx))

    def get_function(self, symbol):
        idx = api.lookup(self.functions, symbol, space.newnil())
        if space.isnil(idx):
            return platform.absent_index()
        return api.to_i(idx)

    def has_possible_static_reference(self, ref):
        return plist.contains_with(self.__static_references, ref, _find_static_ref)

    def add_possible_static_reference(self, ref):
        ref_idx = self.get_scope_reference(ref.name)
        assert not platform.is_absent_index(ref_idx), "Invalid static reference declaration. Reference id not defined"

        self.__static_references = plist.cons(space.newtuple([ref, space.newint(ref_idx)]), self.__static_references)

    def has_operator(self, op_name):
        return api.in_b(self.__operators, op_name)

    def add_operators(self, operators):
        for record in operators:
            op_name = api.at_index(record, 0)
            op = api.at_index(record, 1)
            self.__operators.insert(op_name, op)

    def get_scope_reference(self, name):
        return self.__local_references.get(name)

    def add_scope_reference(self, name):
        assert space.issymbol(name)
        return self.__local_references.add(name)

    def get_scope_literal(self, literal):
        return self.__literals.get(literal)

    def add_scope_literal(self, literal):
        return self.__literals.add(literal)

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
        return self.__locals.insert(local, space.newnil())

    def get_scope_local_index(self, local):
        return api.get_index(self.__locals, local)

    def declared_references(self):
        return self.__local_references.values

    def declared_literals(self):
        return self.__literals.values

    def _create_references(self, prev_scope):
        declared = self.declared_references()
        size = len(declared)
        if size == 0:
            return None

        refs = environment.newreferences_size(size)
        if prev_scope is None:
            return refs

        for static_record in self.__static_references:
            static_ref = api.at_index(static_record, 0)
            static_ref_id = api.to_i(api.at_index(static_record, 1))

            # prev_local_idx = prev_scope.get_scope_local_index(static_ref.name)
            # # local in prev scope overrides static reference
            # if not platform.is_absent_index(prev_local_idx):
            #     continue

            refs._set_refs(static_ref_id, static_ref)

        return refs

    def finalize(self, previous_scope, parse_scope):
        if parse_scope is not None:
            self.add_operators(parse_scope.operators.to_list())

        self.__references = self._create_references(previous_scope)

        return self
        # return space.newscope(self.locals, refs, self.declared_references(),
        #                       self.declared_literals(), self._operators, self._imports,
        #                       self.arg_count, self.is_variadic, self.fn_name_index)

    def create_references(self):
        if self.__references is None:
            return None
        return api.clone(self.__references)

    def create_operators(self):
        if self.__operators is None:
            return None
        return api.clone(self.__operators)

    def create_env_bindings(self):
        return api.clone(self.__locals)
