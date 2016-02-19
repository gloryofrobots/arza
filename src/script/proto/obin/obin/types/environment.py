from obin.types import api, space, plist
from obin.types.root import W_Any, W_Callable
from obin.misc.platform import is_absent_index
from obin.runtime import error


class References(W_Any):
    _virtualizable2_ = ['_refs_[*]']
    _settled_ = True

    def __init__(self, references):
        self._refs_ = references
        self._resizable_ = not bool(len(self._refs_))

    def _to_string_(self):
        return str(self._refs_)

    __str__ = _to_string_

    __repr__ = _to_string_

    def _clone_(self):
        return References([ref for ref in self._refs_])

    def _resize_refs(self, index):
        if index >= len(self._refs_):
            self._refs_ += ([None] * (1 + index - len(self._refs_)))

    def _get_refs(self, index):
        assert index < len(self._refs_)
        assert index >= 0

        if self._resizable_:
            self._resize_refs(index)

        return self._refs_[index]

    def _set_refs(self, index, value):
        if self._resizable_:
            self._resize_refs(index)
        assert index < len(self._refs_)
        assert index >= 0
        self._refs_[index] = value

    def get_ref(self, env, symbol, index):
        # print "get_ref", symbol, index, self._refs_
        ref = self._get_refs(index)
        # print "ref", ref, ref is None
        if ref is None:
            ref = get_reference(env, symbol)
            # print " new ref", ref
            # assert ref is not None
            if space.isnil(ref):
                return error.throw_1(error.Errors.REFERENCE, symbol)
            self._set_refs(index, ref)

        val = ref.get_value()
        if space.isnil(val):
            return error.throw_1(error.Errors.REFERENCE, symbol)
        return val

def newreferences(refs):
    return References(refs)


def newreferences_size(size):
    _refs_ = [None] * size
    return newreferences(_refs_)


class Reference(W_Any):
    _immutable_fields_ = ['env', 'name', 'index']
    _settled_ = True

    def __init__(self, env, referenced, index):
        assert env is not None
        self.env = env
        self.name = referenced
        self.index = index

    def _to_string_(self):
        return api.to_s(self.name)

    __str__ = _to_string_

    __repr__ = _to_string_

    def get_value(self):
        # print "Reference.ref_get_value", self.env, self.index
        return api.at_index(self.env, self.index)


# lookup ref in  environment
def get_reference(env, identifier):
    # print "get_reference lex", lex
    if env is None:
        return space.newnil()

    index = api.get_index(env, identifier)
    if not is_absent_index(index):
        return Reference(env, identifier, index)
    else:
        return get_reference(env.parent_env, identifier)


def get_operator(env, identifier):
    # print "get_reference lex", lex
    undef = space.newnil()
    if env is None:
        return undef
    op = api.lookup(env.operators, identifier, undef)
    if not space.isnil(op):
        return op

    return get_operator(env.parent_env, identifier)


def create_environment(process, source, parent_env):
    if source.env:
        return source.env

    compile_func = W_EnvCompileFunction(source.name, source.bytecode, parent_env)
    process.subprocess(compile_func, space.newnil())

    source.env = compile_func.env
    return source.env


class W_EnvCompileFunction(W_Callable):
    def __init__(self, name, bytecode, parent_env):
        self.name = name
        self.bytecode = bytecode
        self.parent_env = parent_env
        self.env = space.newenv(self.name, self.bytecode.scope, parent_env)

    def _to_routine_(self, stack, args):
        from obin.runtime.routine import create_module_routine
        routine = create_module_routine(self.name, stack, self.bytecode, self.env)
        return routine


class W_EnvSource(W_Any):
    def __init__(self, name, bytecode):
        self.name = name
        self.bytecode = bytecode
        self.env = None


class W_Env(W_Any):
    _immutable_fields_ = ['name', 'parent_env', 'scope', 'literals']

    def __init__(self, name, scope, parent_environment):
        assert isinstance(parent_environment, W_Env) or parent_environment is None
        self.name = name
        self.parent_env = parent_environment
        self.scope = scope
        self.literals = scope.literals
        self.operators = scope.create_operators()
        self.exported_names = scope.exports
        self.refs = scope.create_references()
        self.imports = scope.imports
        self.data = scope.create_env_bindings()
        # TODO MAKE TEST FOR CORRECT STATIC REFS SOMEHOW
        # print "--------------------------ENV------------------------------"
        # print self.refs
        # print scope.reference_names

    def export_all(self):
        self.exported_names = self.data.keys_list()

    def can_export(self, symbol):
        return plist.contains(self.exported_names, symbol)

    def exports(self):
        return self.exported_names

    def get_import(self, index):
        return api.at_index(self.imports, index)

    def ref(self, symbol, index):
        # lookup in self parent environment
        return self.refs.get_ref(self.parent_env, symbol, index)

    def _behavior_(self, process):
        return process.std.behaviors.Environment

    def _put_at_index_(self, idx, v):
        api.put_at_index(self.data, idx, v)

    def _get_index_(self, n):
        return api.get_index(self.data, n)

    def _at_index_(self, i):
        return api.at_index(self.data, i)

    def _put_(self, k, v):
        assert space.issymbol(k)
        api.put(self.data, k, v)

    def _at_(self, n):
        assert space.issymbol(n)
        return api.at(self.data, n)

    def _to_string_(self):
        return self.data._to_string_()
