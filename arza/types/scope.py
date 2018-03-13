from arza.types import space, plist, environment
from arza.types.root import W_Root
from arza.misc import platform
from arza.types import api
from arza.runtime import error

ABSENT = platform.absent_index()


class Symbols:
    def __init__(self, literals):
        self.literals = literals
        self.syms_map = {}
        self.syms_list = []

    def has(self, sym):
        return sym.idx in self.syms_map

    def get(self, sym):
        assert space.issymbol(sym)
        try:
            return self.syms_map[sym.idx]
        except KeyError:
            return ABSENT

    def add(self, sym):
        assert not self.has(sym)
        idx = self.literals.add(sym)
        self.syms_map[sym.idx] = idx
        return idx

    @property
    def values(self):
        return self.syms_list


class Ints:
    def __init__(self, literals):
        self.literals = literals
        self.map = {}
        self.list = []

    def has(self, num):
        return num.int_value in self.map

    def get(self, num):
        assert space.isint(num)
        try:
            return self.map[num.int_value]
        except KeyError:
            return ABSENT

    def add(self, num):
        assert not self.has(num)
        idx = self.literals.add(num)
        self.map[num.int_value] = idx
        return idx

    @property
    def values(self):
        return self.list


class Floats:
    def __init__(self, literals):
        self.literals = literals
        self.map = {}
        self.list = []

    def has(self, num):
        return num.float_value in self.map

    def get(self, num):
        assert space.isfloat(num)
        try:
            return self.map[num.float_value]
        except KeyError:
            return ABSENT

    def add(self, num):
        assert space.isfloat(num)
        assert not self.has(num)
        idx = self.literals.add(num)
        self.map[num.float_value] = idx
        return idx

    @property
    def values(self):
        return self.list


class Chars:
    def __init__(self, literals):
        self.literals = literals
        self.map = {}
        self.list = []

    def has(self, num):
        return num.char_value in self.map

    def get(self, num):
        assert space.ischar(num)
        try:
            return self.map[num.char_value]
        except KeyError:
            return ABSENT

    def add(self, num):
        assert space.ischar(num)
        assert not self.has(num)
        idx = self.literals.add(num)
        self.map[num.char_value] = idx
        return idx

    @property
    def values(self):
        return self.list


class Strings:
    def __init__(self, literals):
        self.literals = literals
        self.map = {}
        self.list = []

    def has(self, num):
        return num.string_value in self.map

    def get(self, num):
        assert space.isstring(num)
        try:
            return self.map[num.string_value]
        except KeyError:
            return ABSENT

    def add(self, num):
        assert space.isstring(num)
        assert not self.has(num)
        idx = self.literals.add(num)
        self.map[num.string_value] = idx
        return idx

    @property
    def values(self):
        return self.list


class Literals:
    def __init__(self):
        self.values = []

    def at(self, idx):
        return self.values[idx]

    def get(self, val):
        return ABSENT

    def add(self, val):
        self.values = self.values + [val]
        return len(self.values) - 1


class ScopeSet:
    def __init__(self):
        # TODO USE PLIST
        self.values = []

    def get(self, val):
        try:
            idx = self.values.index(val)
            # print "FIND", idx, val
            return idx
        except ValueError:
            # print "NOT FIND", val
            return platform.absent_index()

    def add(self, val):
        assert val not in self.values, (val, self.values)
        self.values = self.values + [val]
        return len(self.values) - 1


def _find_static_ref(ref1, ref2):
    # ref2 is tuple (ref, idx)
    return api.equal_b(ref1.name, api.at_index(ref2, 0).name)


def _find_function(symbol, record):
    return api.equal_b(symbol, api.at_index(record, 0))


class W_Scope(W_Root):
    def __init__(self):
        self.__locals = space.newassocarray()

        self.__temp_index = 0

        self.__literals = Literals()
        self.__floats = Floats(self.__literals)
        self.__ints = Ints(self.__literals)
        self.__chars = Chars(self.__literals)
        self.__strings = Strings(self.__literals)
        self.__symbols = Symbols(self.__literals)

        self.__local_references = ScopeSet()
        self.__operators = space.newassocarray()
        self.__declared_exports = plist.empty()
        self.__static_references = plist.empty()

        self.imports = space.newassocarray()
        self.functions = space.newassocarray()
        self.arg_count = -1
        self.references = None
        self.is_variadic = None
        self.exports = None

    ######################################################
    def add_temporary(self):
        idx = self.__temp_index
        self.__temp_index += 1
        return idx

    def has_temporary(self, idx):
        return idx >= 0 and idx < self.__temp_index

    def what_next_temporary(self):
        return self.__temp_index

    ###########################

    def add_export(self, name):
        assert space.issymbol(name)
        assert not self.has_export(name)
        self.__declared_exports = plist.cons(name, self.__declared_exports)

    def has_export(self, name):
        assert space.issymbol(name)
        return plist.contains(self.__declared_exports, name)

    ###########################

    def add_imported(self, name, func):
        assert space.issymbol(name)
        assert platform.is_absent_index(self.get_imported_index(name))
        return self.imports.insert(name, func)

    def get_imported_index(self, name):
        return api.get_index(self.imports, name)

    ###########################

    def add_function(self, symbol, idx):
        self.functions.insert(symbol, space.newint(idx))

    def get_function(self, symbol):
        idx = api.lookup(self.functions, symbol, space.newvoid())
        if space.isvoid(idx):
            return platform.absent_index()
        return api.to_i(idx)

    ###########################

    def has_possible_static_reference(self, ref):
        return plist.contains_with(self.__static_references, ref, _find_static_ref)

    def add_possible_static_reference(self, ref):
        ref_idx = self.get_scope_reference(ref.name)
        assert not platform.is_absent_index(ref_idx), "Invalid static reference declaration. Reference id not defined"

        self.__static_references = plist.cons(space.newtuple([ref, space.newint(ref_idx)]), self.__static_references)

    ###########################

    def has_operator(self, op_name):
        return api.contains_b(self.__operators, op_name)

    def add_operators(self, operators):
        for record in operators:
            op_name = api.at_index(record, 0)
            op = api.at_index(record, 1)
            self.__operators.insert(op_name, op)

    ###########################

    def get_scope_reference(self, name):
        return self.__local_references.get(name)

    def add_scope_reference(self, name):
        assert space.issymbol(name)
        return self.__local_references.add(name)

    ###########################
    def get_scope_literal_value(self, idx):
        return self.__literals.at(idx)

    def get_scope_literal(self, literal):
        return self.__literals.get(literal)

    def add_scope_literal(self, literal):
        return self.__literals.add(literal)

    ###########################

    def get_scope_symbol(self, literal):
        return self.__symbols.get(literal)

    def add_scope_symbol(self, literal):
        return self.__symbols.add(literal)

    ###########################

    def get_string(self, literal):
        return self.__strings.get(literal)

    def add_string(self, literal):
        return self.__strings.add(literal)

    ###########################

    def get_char(self, literal):
        return self.__chars.get(literal)

    def add_char(self, literal):
        return self.__chars.add(literal)

    ###########################

    def get_int(self, literal):
        return self.__ints.get(literal)

    def add_int(self, literal):
        return self.__ints.add(literal)

    ###########################

    def get_float(self, literal):
        return self.__floats.get(literal)

    def add_float(self, literal):
        return self.__floats.add(literal)

    ###########################

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
        return self.__locals.insert(local, space.newvoid())

    def get_scope_local_index(self, local):
        return api.get_index(self.__locals, local)

    def has_local(self, local):
        return not platform.is_absent_index(api.get_index(self.__locals, local))

    def _create_references(self, prev_scope):
        declared = self.__local_references.values
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

    def _create_exports(self):
        if plist.is_empty(self.__declared_exports):
            SKIPPED = "_"
            syms = []
            keys = self.__locals.keys_list()

            for key in keys:
                if key.string.startswith_s(SKIPPED):
                    continue
                syms.append(key)
            return space.newlist(syms)

        for exported in self.__declared_exports:
            if not self.has_local(exported):
                error.throw_2(error.Errors.EXPORT_ERROR, space.newstring(u"Unreachable export variable"), exported)

        return self.__declared_exports

    def finalize(self, previous_scope, parse_scope):
        if parse_scope is not None:
            self.add_operators(parse_scope.operators.to_list())

        self.exports = self._create_exports()
        self.references = self._create_references(previous_scope)

        return self

    def create_references(self):
        if self.references is None:
            return None
        return api.clone(self.references)

    def create_operators(self):
        if self.__operators is None:
            return None
        return api.clone(self.__operators)

    def create_env_bindings(self):
        return api.clone(self.__locals)

    def create_temporaries(self):
        if self.__temp_index == 0:
            return None
        return [space.newvoid() for _ in range(self.__temp_index)]

    # FINAL GETTERS

    def literals(self):
        return self.__literals.values
