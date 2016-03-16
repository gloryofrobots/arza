__author__ = 'gloryofrobots'
from obin.compile.code.opcode import *
from obin.compile.parse import parser
from obin.compile.parse import nodes
from obin.compile.parse.nodes import (node_type, node_arity,
                                      node_first, node_second, node_third, node_fourth, node_children, is_empty_node)
from obin.compile.parse.node_type import *
from obin.types import space, api, plist, environment, symbol as symbols, string as strings
from obin.compile.code.source import CodeSource, codeinfo, codeinfo_unknown, SourceInfo
from obin.misc import platform, strutil
from obin.runtime import error
from obin.builtins import lang_names


# TODO REMOVE NIL as token and node_type
# TODO OPTIMISE STORE_LOCAL

def compile_error(compiler, code, node, message):
    line = code.info.get_line(api.to_i(nodes.node_line(node)))
    return error.throw(error.Errors.COMPILE_ERROR,
                       space.newtuple([
                           space.newstring(message),
                           space.newint(nodes.node_type(node)),
                           space.newstring_s(nodes.node_value_s(node)),
                           space.newtuple([space.newstring(u"line"), nodes.node_line(node),
                                           space.newstring(u"column"), nodes.node_column(node)]),
                           space.newstring(line)
                       ]))


class Compiler:
    def __init__(self, process, env, path, src):
        self.process = process
        self.env = env
        self.scopes = []
        self.source_path = path
        self.source = src


def info(node):
    if is_empty_node(node):
        return codeinfo_unknown()
    return codeinfo(nodes.node_position(node), nodes.node_line(node), nodes.node_column(node))


########################
# SCOPES
########################


def _enter_scope(compiler):
    new_scope = space.newscope()
    compiler.scopes.append(new_scope)


def _exit_scope(compiler):
    compiler.scopes.pop()


def _current_scope(compiler):
    return compiler.scopes[-1]


def _previous_scope(compiler):
    if len(compiler.scopes) == 1:
        return None

    return compiler.scopes[-2]


def _is_modifiable_binding(compiler, name):
    scope = _current_scope(compiler)
    if not platform.is_absent_index(scope.get_scope_local_index(name)):
        return True

    return False


def _declare_arguments(compiler, args_count, varargs):
    _current_scope(compiler).declare_scope_arguments(args_count, varargs)


def _declare_reference(compiler, symbol):
    assert space.issymbol(symbol)
    scope = _current_scope(compiler)
    idx = scope.get_scope_reference(symbol)
    if platform.is_absent_index(idx):
        idx = scope.add_scope_reference(symbol)
    return idx


def _declare_static_reference(compiler, ref):
    scope = _current_scope(compiler)
    if scope.has_possible_static_reference(ref):
        return

    # print "REF", ref.name
    scope.add_possible_static_reference(ref)


def _declare_literal(compiler, literal):
    assert space.isany(literal)
    scope = _current_scope(compiler)
    idx = scope.get_scope_literal(literal)
    if platform.is_absent_index(idx):
        idx = scope.add_scope_literal(literal)
    return idx


def _declare_temporary(compiler):
    scope = _current_scope(compiler)
    return scope.add_temporary()


def _has_temporary(compiler, idx):
    scope = _current_scope(compiler)
    return scope.has_temporary(idx)


def _declare_local(compiler, symbol):
    assert space.issymbol(symbol)
    assert not api.isempty(symbol)
    scope = _current_scope(compiler)
    idx = scope.get_scope_local_index(symbol)
    if not platform.is_absent_index(idx):
        return idx

    idx = scope.add_scope_local(symbol)
    assert not platform.is_absent_index(idx)
    return idx


def _declare_export(compiler, code, node):
    name = _get_symbol_name(compiler, node)
    scope = _current_scope(compiler)
    if scope.has_export(name):
        compile_error(compiler, code, node, u"Name has already exported")

    scope.add_export(name)


def _declare_import(compiler, name, func):
    assert space.issymbol(name)
    assert not api.isempty(name)
    scope = _current_scope(compiler)
    idx = scope.get_imported_index(name)
    if not platform.is_absent_index(idx):
        return idx

    idx = scope.add_imported(name, func)
    assert not platform.is_absent_index(idx)
    return idx


def _declare_function(compiler, code, node):
    symbol = _get_symbol_name_or_empty(compiler.process, node)
    scope = _current_scope(compiler)
    idx = scope.get_scope_local_index(symbol)
    if not platform.is_absent_index(idx):
        compile_error(compiler, code, node, u"Name has already assigned")

    idx = scope.add_scope_local(symbol)
    scope.add_function(symbol, idx)
    return idx


def _get_function_index(compiler, symbol):
    scope = _current_scope(compiler)
    idx = scope.get_function(symbol)

    # TODO make two compiler passes
    # non statement function like fun f-> end ()
    if platform.is_absent_index(idx):
        return _declare_local(compiler, symbol)
    return idx


def _get_variable_index(compiler, code, node, name):
    assert space.issymbol(name)
    """
        return var_index, is_local_variable
    """
    scope_id = 0
    for scope in reversed(compiler.scopes):
        idx = scope.get_scope_local_index(name)
        if not platform.is_absent_index(idx):
            if scope_id == 0:
                return idx, True
            else:
                # TODO here can be optimisation where we can calculate number of scopes to find back variable
                ref_id = _declare_reference(compiler, name)
                return ref_id, False
        scope_id += 1

    ref_id = _declare_reference(compiler, name)

    ref = environment.get_reference(compiler.env, name)
    if space.isvoid(ref):
        names_s = api.to_s(name)
        # HACK for late binding of internal names in prelude

        if not names_s.startswith(lang_names.PREFIX):
            for name in _current_scope(compiler).imports.keys():
                print name
            return compile_error(compiler, code, node, u"Unreachable variable")
    else:
        _declare_static_reference(compiler, ref)

    return ref_id, False


# *******************************************************
# EMIT HELPERS *******************************************
# **************************************************
def _emit_call(compiler, code, node, arg_count, funcname):
    func = nodes.create_name_node_s(node, funcname)
    _compile(compiler, code, func)
    code.emit_1(CALL, arg_count, info(node))


def _emit_store_name(compiler, code, namenode):
    name = _get_symbol_name(compiler, namenode)
    # name = space.newsymbol_s(compiler.process, nodes.node_value_s(namenode))
    _emit_store(compiler, code, name, namenode)


def _emit_store(compiler, code, name, namenode):
    index = _declare_local(compiler, name)

    name_index = _declare_literal(compiler, name)
    code.emit_2(STORE_LOCAL, index, name_index, info(namenode))


def _emit_pop(code):
    code.emit_0(POP, codeinfo_unknown())


def _emit_dup(code):
    code.emit_0(DUP, codeinfo_unknown())


def _emit_void(code):
    code.emit_0(VOID, codeinfo_unknown())


def _emit_empty_list(code):
    code.emit_1(LIST, 0, codeinfo_unknown())


def _emit_literal(compiler, code, node, literal):
    idx = _declare_literal(compiler, literal)
    code.emit_1(LITERAL, idx, info(node))
    return idx


def _emit_literal_index(compiler, code, node, idx):
    code.emit_1(LITERAL, idx, info(node))


def _emit_symbol_literal(compiler, code, name):
    symbol = _get_symbol_name(compiler, name)
    return _emit_literal(compiler, code, name, symbol)


def _emit_fself(compiler, code, node, name):
    code.emit_0(FSELF, info(node))
    _emit_store(compiler, code, name, node)


def _emit_integer(compiler, code, integer):
    idx = _declare_literal(compiler, space.newint(integer))
    code.emit_1(LITERAL, idx, codeinfo_unknown())


# ********************************************
# EXTRACTORS ***********************************************
# ************************************************

def _get_unquoted_value(node):
    # REMOVE BACKTICKS `xxx`
    return nodes.node_value_s(node)[1:len(nodes.node_value_s(node)) - 1]


def _get_symbol_or_name_value(name):
    ntype = node_type(name)
    if ntype == NT_SYMBOL:
        return _get_name_value(node_first(name))
    elif ntype == NT_IMPORTED_NAME:
        return _module_path_to_string(name)
    else:
        return _get_name_value(name)


def _get_name_value(name):
    ntype = node_type(name)
    if ntype == NT_SYMBOL:
        return _get_name_value(node_first(name))
    elif ntype == NT_STR:
        value = _get_unquoted_value(name)
    elif ntype == NT_NAME:
        value = nodes.node_value_s(name)
    else:
        assert False, ("_get_name_value", ntype)
    return value


def _get_symbol_name(compiler, name):
    sym = _get_symbol_or_name_value(name)
    return space.newsymbol_s(compiler.process, sym)


def _get_symbol_name_or_empty(process, name):
    if is_empty_node(name):
        return space.newsymbol(process, u"")
    else:
        return space.newsymbol_s(process, nodes.node_value_s(name))


# *********************************************
# COMPILERS
# **************************************

def _compile_FLOAT(compiler, code, node):
    value = float(nodes.node_value_s(node))
    idx = _declare_literal(compiler, space.newfloat(value))
    code.emit_1(LITERAL, idx, info(node))


def _compile_INT(compiler, code, node):
    value = strutil.string_to_int(nodes.node_value_s(node))
    idx = _declare_literal(compiler, space.newnumber(value))
    code.emit_1(LITERAL, idx, info(node))


def _compile_TRUE(compiler, code, node):
    code.emit_0(TRUE, info(node))


def _compile_FALSE(compiler, code, node):
    code.emit_0(FALSE, info(node))


def _compile_STR(compiler, code, node):
    from obin.runistr import unicode_unescape, decode_str_utf8

    try:
        strval = str(nodes.node_value_s(node))
        strval = decode_str_utf8(strval)
        strval = strutil.unquote_s(strval)
        strval = unicode_unescape(strval)
        string = space.newstring(strval)
        idx = _declare_literal(compiler, string)
        code.emit_1(LITERAL, idx, info(node))
    except RuntimeError as e:
        compile_error(compiler, code, node, unicode(e.args[0]))


def _compile_CHAR(compiler, code, node):
    from obin.runistr import unicode_unescape, decode_str_utf8
    # TODO CHAR

    try:
        strval = str(nodes.node_value_s(node))
        strval = decode_str_utf8(strval)
        strval = strutil.unquote_s(strval)
        strval = unicode_unescape(strval)
        string = space.newstring(strval)
        idx = _declare_literal(compiler, string)
        code.emit_1(LITERAL, idx, info(node))
    except RuntimeError as e:
        compile_error(compiler, code, node, unicode(e.args[0]))


def _compile_AND(compiler, code, node):
    _compile(compiler, code, node_first(node))
    one = code.prealocate_label()
    code.emit_1(JUMP_IF_FALSE_NOPOP, one, info(node))
    _compile(compiler, code, node_second(node))
    code.emit_1(LABEL, one, info(node))


def _compile_OR(compiler, code, node):
    _compile(compiler, code, node_first(node))
    one = code.prealocate_label()
    code.emit_1(JUMP_IF_TRUE_NOPOP, one, info(node))
    _compile(compiler, code, node_second(node))
    code.emit_1(LABEL, one, info(node))


#########################################################

PATTERN_DATA = """
    match (1,2)
        case (a, b) -> a + b
        case (x, y) -> a - b
    end
"""


def _compile_match(compiler, code, node, patterns, error_code):
    from obin.compile.match import transform
    from obin.compile.parse.nodes import create_goto_node
    temp_idx = _declare_temporary(compiler)
    code.emit_1(STORE_TEMPORARY, temp_idx, codeinfo_unknown())

    endmatch = code.prealocate_label()

    graph = transform(compiler, code, node, patterns, create_goto_node(endmatch), temp_idx)
    _compile(compiler, code, graph)

    # Allocate error in case of no match
    err_node = nodes.create_match_fail_node(node, str(error_code), temp_idx)
    _compile(compiler, code, err_node)
    code.emit_0(THROW, info(node))

    code.emit_1(LABEL, endmatch, codeinfo_unknown())


def _compile_MATCH(compiler, code, node):
    exp = node_first(node)
    patterns = node_second(node)
    _compile(compiler, code, exp)
    _compile_match(compiler, code, node, patterns, error.Errors.MATCH_ERROR)


def _compile_UNDEFINE(compiler, code, node):
    varname = node_first(node)
    name = _get_symbol_name(compiler, varname)
    _emit_void(code)
    _emit_store(compiler, code, name, node)


def _compile_GOTO(compiler, code, node):
    # TODO REMOVE THIS SHIT
    # WE NEED TO REMOVE POPS ON GOTO BECAUSE OF AUTOMATIC POP INSERTION
    # GOTO USED ONLY FOR JUMPS ON PATTERN MATCHING BECAUSE IN PM WE PRODUCE TREE OF IFS
    # AND NEED JUMP FROM SUCCESS BRANCH. IT'S ACTUALLY SIMPLIFIES COMPILATION BUT LEEDS TO THIS BAD DESIGN
    # SOLUTION: REMOVE AUTO POPS, SOMEHOW

    last_code = code.last()
    if last_code[0] == POP:
        code.remove_last()

    value = int(nodes.node_value_s(node))
    code.emit_1(JUMP, value, codeinfo_unknown())


#########################################################
#####
# DESTRUCT ASSIGN
####
def _compile_destruct(compiler, code, left, exp):
    _compile(compiler, code, exp)

    if node_type(left) != NT_TUPLE or not _is_optimizable_unpack_seq_pattern(left):
        compile_error(compiler, code, left, u"Invalid tuple unpack")
    else:
        _compile_destruct_unpack_seq(compiler, code, left)


def _is_optimizable_unpack_seq_pattern(node):
    items = node_first(node)
    for child in items:
        if node_type(child) != NT_NAME:
            return False
    return True


def _compile_destruct_unpack_seq(compiler, code, node):
    _emit_dup(code)
    names = node_first(node)
    length = len(names)
    code.emit_1(UNPACK_TUPLE, length, info(node))
    if length > 1:
        for name in names[0:length - 1]:
            _emit_store_name(compiler, code, name)
            _emit_pop(code)
    last_name = names[length - 1]
    _emit_store_name(compiler, code, last_name)
    _emit_pop(code)


################################################################################

def _compile_ASSIGN(compiler, code, node):
    left = node_first(node)
    exp = node_second(node)

    ntype = node_type(left)
    if ntype == NT_NAME:
        # print "NAME ASSIGN"
        _compile(compiler, code, exp)
        _emit_store_name(compiler, code, left)
    elif is_simple_pattern(left, False):
        # print "DESTRUCT ASSIGN"
        return _compile_destruct(compiler, code, left, exp)
    else:
        # print " MATCH ASSIGN"
        scope = _current_scope(compiler)
        idx = scope.what_next_temporary()
        exp_node = nodes.create_temporary_node(node, idx)
        match = nodes.create_match_node(node, exp, [nodes.list_node(
            [left, nodes.list_node([exp_node])]
        )])
        _compile(compiler, code, match)


def _compile_node_name_lookup(compiler, code, node):
    name = _get_symbol_name(compiler, node)

    index, is_local = _get_variable_index(compiler, code, node, name)
    name_index = _declare_literal(compiler, name)
    if is_local:
        code.emit_2(LOCAL, index, name_index, info(node))
    else:
        code.emit_2(OUTER, index, name_index, info(node))


def _compile_TEMPORARY(compiler, code, node):
    idx_node = node_first(node)
    idx = api.to_i(idx_node)
    if not _has_temporary(compiler, idx):
        compile_error(compiler, code, node, u"Invalid temporary variable %d" % idx)
    code.emit_1(TEMPORARY, idx, info(node))


def _compile_NAME(compiler, code, node):
    _compile_node_name_lookup(compiler, code, node)


def _compile_SYMBOL(compiler, code, node):
    name = node_first(node)
    _emit_symbol_literal(compiler, code, name)


def _compile_THROW(compiler, code, node):
    expr = node_first(node)
    _compile(compiler, code, expr)
    code.emit_0(THROW, info(node))


# TODO MAKE NAMES from SYMBOLS in parser
def _emit_map_key(compiler, code, key):
    if node_type(key) == NT_NAME:
        # in case of names in object literal we must convert them to symbols
        _emit_symbol_literal(compiler, code, key)
    else:
        _compile(compiler, code, key)


def _transform_modify(compiler, node, func, source, modifications):
    """
    transforms modify x.{a=1, b=2, 0=4} into series of puts
    put 0 4 (put b 2 (put a 1 x))
    """
    if plist.is_empty(modifications):
        return source

    m, tail = plist.split(modifications)
    key = m[0]
    value = m[1]

    if node_type(key) == NT_NAME:
        key = nodes.create_symbol_node(key, key)
    return _transform_modify(compiler, node,
                             func,
                             nodes.create_call_node_3(node, func, key, value, source),
                             tail)


def _compile_MODIFY(compiler, code, node):
    call = _transform_modify(compiler, node,
                             nodes.create_name_node_s(node, lang_names.PUT),
                             node_first(node),
                             node_second(node))
    _compile(compiler, code, call)


def _compile_MAP(compiler, code, node):
    items = node_first(node)
    for c in items:
        key = c[0]
        value = c[1]
        if is_empty_node(value):
            compile_error(compiler, code, node, u"Value expected")
        else:
            _compile(compiler, code, value)

        _emit_map_key(compiler, code, key)

    code.emit_1(MAP, len(items), info(node))


def _compile_TUPLE(compiler, code, node):
    items = node_first(node)
    for c in items:
        _compile(compiler, code, c)

    code.emit_1(TUPLE, len(items), info(node))


def _compile_UNIT(compiler, code, node):
    code.emit_1(TUPLE, 0, info(node))


def _compile_LIST(compiler, code, node):
    items = node_first(node)
    for c in items:
        _compile(compiler, code, c)

    code.emit_1(LIST, len(items), info(node))


def _compile_func_args_and_body(compiler, code, name, params, body):
    funcname = _get_symbol_name_or_empty(compiler.process, name)
    _enter_scope(compiler)

    funccode = newcode(compiler)

    if node_type(params) == NT_UNIT:
        _declare_arguments(compiler, 0, False)
    else:
        args = node_first(params)
        length = len(args)
        funccode.emit_0(FARGS, codeinfo_unknown())

        last_param = args[length - 1]
        is_variadic = True if node_type(last_param) == NT_REST else False
        _declare_arguments(compiler, length, is_variadic)
        _compile_destruct_unpack_seq(compiler, funccode, params)

    if not api.isempty(funcname):
        _emit_fself(compiler, funccode, name, funcname)

    _compile_2(compiler, funccode, body)
    current_scope = _current_scope(compiler)
    scope = current_scope.finalize(_previous_scope(compiler), None)
    _exit_scope(compiler)
    # print "LOCALS:", str(scope.variables.keys())
    # print "REFS:", str(scope.references)
    compiled_code = funccode.finalize_compilation(scope)
    # print [str(c) for c in compiled_code.opcodes]
    # print "-------------------------"

    source = space.newfuncsource(funcname, compiled_code)
    source_index = _declare_literal(compiler, source)
    code.emit_1(FUNCTION, source_index, info(name))


def _compile_case_function(compiler, code, node, name, cases):
    funcname = _get_symbol_name_or_empty(compiler.process, name)
    _enter_scope(compiler)

    funccode = newcode(compiler)

    _declare_arguments(compiler, 0, True)

    if not api.isempty(funcname):
        _emit_fself(compiler, funccode, name, funcname)

    funccode.emit_0(FARGS, codeinfo_unknown())
    _compile_match(compiler, funccode, node, cases, error.Errors.FUNCTION_MATCH_ERROR)
    current_scope = _current_scope(compiler)
    scope = current_scope.finalize(_previous_scope(compiler), None)
    _exit_scope(compiler)

    compiled_code = funccode.finalize_compilation(scope)

    source = space.newfuncsource(funcname, compiled_code)
    source_index = _declare_literal(compiler, source)
    code.emit_1(FUNCTION, source_index, info(node))


def is_simple_pattern(pattern, allow_unit):
    ntype = node_type(pattern)
    if ntype == NT_TUPLE:
        for child in node_first(pattern):
            if node_type(child) != NT_NAME:
                return False
        return True
    elif ntype == NT_UNIT and allow_unit is True:
        return True
    return False


def _compile_FUN(compiler, code, node):
    namenode = node_first(node)
    funcname = _get_symbol_name_or_empty(compiler.process, namenode)

    funcs = node_second(node)
    # single function
    if len(funcs) == 1:
        func = funcs[0]
        params = func[0]
        body = func[1]
        if not is_simple_pattern(params, True):
            _compile_case_function(compiler, code, node, namenode, funcs)
        else:
            # print "SIMPLE FUNC", funcname
            _compile_func_args_and_body(compiler, code, namenode, params, body)
    else:
        _compile_case_function(compiler, code, node, namenode, funcs)

    if api.isempty(funcname):
        return

    # index = _get_function_index(compiler, funcname)
    index = _declare_local(compiler, funcname)

    funcname_index = _declare_literal(compiler, funcname)
    code.emit_2(STORE_LOCAL, index, funcname_index, info(node))


def _compile_branch(compiler, code, condition, body, endif):
    _compile(compiler, code, condition)
    end_body = code.prealocate_label()
    code.emit_1(JUMP_IF_FALSE, end_body, info(condition))
    _compile(compiler, code, body)
    code.emit_1(JUMP, endif, codeinfo_unknown())
    code.emit_1(LABEL, end_body, codeinfo_unknown())


def _compile_WHEN(compiler, code, node):
    condition = node_first(node)
    truebranch = node_second(node)
    falsebranch = node_third(node)
    endif = code.prealocate_label()
    _compile_branch(compiler, code, condition, truebranch, endif)
    _compile(compiler, code, falsebranch)
    code.emit_1(LABEL, endif, codeinfo_unknown())


def _compile_WHEN_NO_ELSE(compiler, code, node):
    condition = node_first(node)
    body = node_second(node)
    endif = code.prealocate_label()
    _compile_branch(compiler, code, condition, body, endif)
    _emit_void(code)
    code.emit_1(LABEL, endif, codeinfo_unknown())


def _compile_CONDITION(compiler, code, node):
    branches = node_first(node)

    endif = code.prealocate_label()
    length = len(branches)
    for i in range(length - 1):
        branch = branches[i]
        _compile_branch(compiler, code, branch[0], branch[1], endif)

    elsebranch = branches[length - 1]
    _compile(compiler, code, elsebranch[1])
    code.emit_1(LABEL, endif, codeinfo_unknown())


def _compile_TRY(compiler, code, node):
    trynode = node_first(node)
    catches = node_second(node)

    finallynode = node_third(node)
    finallylabel = code.prealocate_label()

    catchlabel = code.prealocate_label()
    code.emit_1(PUSH_CATCH, catchlabel, codeinfo_unknown())
    _compile(compiler, code, trynode)
    code.emit_0(POP_CATCH, codeinfo_unknown())
    code.emit_1(JUMP, finallylabel, codeinfo_unknown())

    # exception on top of the stack due to internal process/routine logic
    code.emit_1(LABEL, catchlabel, codeinfo_unknown())
    _compile_match(compiler, code, node, catches, error.Errors.EXCEPTION_MATCH_ERROR)

    code.emit_1(JUMP, finallylabel, codeinfo_unknown())
    code.emit_1(LABEL, finallylabel, codeinfo_unknown())
    if not is_empty_node(finallynode):
        _compile(compiler, code, finallynode)


def _compile_EXPORT(compiler, code, node):
    name_node = node_first(node)
    names = node_first(name_node)
    for name in names:
        _declare_export(compiler, code, name)


############################
# IMPORT
#############################

def _compile_LOOKUP_MODULE(compiler, code, node):
    _compile_node_name_lookup(compiler, code, node)


def _module_path_to_string(node):
    if node_type(node) == NT_IMPORTED_NAME:
        return _module_path_to_string(node_first(node)) + ':' + nodes.node_value_s(node_second(node))
    else:
        return nodes.node_value_s(node)


def _get_import_data_and_emit_module(compiler, code, node):
    from obin.runtime import load
    exp = node_first(node)
    names = node_second(node)

    if node_type(exp) == NT_AS:
        import_name = node_second(exp)
        module_path = _module_path_to_string(node_first(exp))
    elif node_type(exp) == NT_IMPORTED_NAME:
        import_name = node_second(exp)
        module_path = _module_path_to_string(exp)
    else:
        assert node_type(exp) == NT_NAME
        import_name = exp
        module_path = nodes.node_value_s(exp)

    import_name_s = _get_symbol_name(compiler, import_name)
    module = load.import_module(compiler.process, space.newsymbol_s(compiler.process, module_path))
    var_names = []
    exports = module.exports()
    if is_empty_node(names):
        _var_names = exports
        for _name in _var_names:
            var_names.append((_name, _name))
    else:
        for _name_node in node_first(names):
            if node_type(_name_node) == NT_NAME:
                _name = _get_symbol_name(compiler, _name_node)
                _bind_name = _name
            elif node_type(_name_node) == NT_AS:
                _name = _get_symbol_name(compiler, node_first(_name_node))
                _bind_name = _get_symbol_name(compiler, node_second(_name_node))
            else:
                assert False

            if not module.can_export(_name):
                compile_error(compiler, code, node, u"Invalid import name %s. Please, check source module export list"
                              % api.to_u(_name))
            var_names.append((_name, _bind_name))

    module_literal = _declare_literal(compiler, module)
    code.emit_1(LITERAL, module_literal, info(node))
    return module, import_name_s, var_names


def _emit_imported(compiler, code, node, module, var_name, bind_name, is_pop):
    func = api.at(module, var_name)
    idx = _declare_import(compiler, bind_name, func)
    code.emit_1(IMPORT_NAME, idx, info(node))
    # print "IMPORT", bind_name, var_name
    _emit_store(compiler, code, bind_name, node)
    if is_pop:
        _emit_pop(code)


def _compile_IMPORT(compiler, code, node):
    colon = space.newsymbol(compiler.process, u":")
    module, import_name, var_names = _get_import_data_and_emit_module(compiler, code, node)
    i = 0
    last_index = len(var_names) - 1
    for var_name, bind_name in var_names:
        full_bind_name = symbols.concat_3(compiler.process, import_name, colon, bind_name)
        need_pop = False if i == last_index else True
        _emit_imported(compiler, code, node, module, var_name, full_bind_name, need_pop)
        i += 1


def _compile_IMPORT_FROM(compiler, code, node):
    module, import_name, var_names = _get_import_data_and_emit_module(compiler, code, node)
    i = 0
    last_index = len(var_names) - 1
    for var_name, bind_name in var_names:
        need_pop = False if i == last_index else True
        _emit_imported(compiler, code, node, module, var_name, bind_name, need_pop)
        i += 1


def _delete_hiding_names(compiler, code, node, module, var_names):
    exports = module.exports()
    imported = []
    deleted = [var[0] for var in var_names]

    for name in exports:
        if name in deleted:
            continue
        imported.append(name)
    return imported


def _compile_IMPORT_HIDING(compiler, code, node):
    colon = space.newsymbol(compiler.process, u":")
    module, import_name, var_names = _get_import_data_and_emit_module(compiler, code, node)
    var_names = _delete_hiding_names(compiler, code, node, module, var_names)
    i = 0
    last_index = len(var_names) - 1
    for var_name in var_names:
        bind_name = symbols.concat_3(compiler.process, import_name, colon, var_name)
        need_pop = False if i == last_index else True
        _emit_imported(compiler, code, node, module, var_name, bind_name, need_pop)
        i += 1


def _compile_IMPORT_FROM_HIDING(compiler, code, node):
    module, import_name, var_names = _get_import_data_and_emit_module(compiler, code, node)
    var_names = _delete_hiding_names(compiler, code, node, module, var_names)
    i = 0
    last_index = len(var_names) - 1
    for var_name in var_names:
        need_pop = False if i == last_index else True
        _emit_imported(compiler, code, node, module, var_name, var_name, need_pop)
        i += 1


def _compile_MODULE(compiler, code, node):
    raise DeprecationWarning("inner modules not supported")
    # name_node = node_first(node)
    # body = node_second(node)
    # parse_scope = node_third(node)
    #
    # compiled_code = compile_ast(compiler, body, parse_scope)
    #
    # module_name = _get_symbol_name(compiler, name_node)
    # module = space.newenvsource(module_name, compiled_code)
    # module_index = _declare_literal(compiler, module)
    # code.emit_1(MODULE, module_index, info(node))
    #
    # _emit_store(compiler, code, module_name, name_node)


def _compile_FENV(compiler, code, node):
    code.emit_0(FENV, info(node))


def _declare_local_name(compiler, code, node):
    sym = space.newsymbol_s(compiler.process, nodes.node_value_s(node))
    name_index = _declare_literal(compiler, sym)
    index = _declare_local(compiler, sym)
    return sym, index, name_index


def _compile_DERIVE(compiler, code, node):
    traits = node_first(node)
    types = node_second(node)
    _compile(compiler, code, traits)
    _compile(compiler, code, types)

    _emit_call(compiler, code, node, 2, lang_names.DERIVE)


def _compile_UNION(compiler, code, node):
    union_name = node_first(node)
    # first arg
    _emit_symbol_literal(compiler, code, union_name)

    types = node_second(node)

    for _type in types:
        _compile_TYPE(compiler, code, _type)

    # second arg
    code.emit_1(LIST, len(types), info(node))

    _emit_call(compiler, code, node, 2, lang_names.UNION)


def _compile_TYPE(compiler, code, node):
    # compiles to call to type function instead of some opcode
    name_node = node_first(node)

    # first arg
    _emit_symbol_literal(compiler, code, name_node)

    # second arg
    fields = node_second(node)
    # third arg
    constructor = node_third(node)

    if is_empty_node(fields):
        _emit_empty_list(code)
        _emit_void(code)
    else:
        _compile(compiler, code, fields)
        _compile_case_function(compiler, code, node, nodes.empty_node(), constructor)

    _emit_call(compiler, code, node, 3, lang_names.TYPE)
    _emit_store_name(compiler, code, name_node)


def _compile_TRAIT(compiler, code, node):
    trait_name_node = node_first(node)
    var_name_node = node_second(node)
    constraints_node = node_third(node)

    _emit_symbol_literal(compiler, code, trait_name_node)
    _emit_symbol_literal(compiler, code, var_name_node)
    _compile(compiler, code, constraints_node)

    _emit_call(compiler, code, node, 3, lang_names.TRAIT)
    _emit_store_name(compiler, code, trait_name_node)

    methods = node_fourth(node)
    last_index = len(methods) - 1

    method_locals = []
    # DECLARE METHODS FIRST TO ALLOW DEFAULT IMPLEMENTATION USE ALL TRAIT METHODS
    for i, method in enumerate(methods):
        method_name_node = method[0]
        method_name, method_index, method_name_index = _declare_local_name(compiler, code, method_name_node)
        method_locals.append((method_name, method_index, method_name_index))

    for i, method in enumerate(methods):
        # duplicate trait on top
        _emit_dup(code)

        method_sig = method[1]
        method_default_impl = method[2]
        local_info = method_locals[i]
        method_name, method_index, method_name_index = local_info

        _emit_literal_index(compiler, code, node, method_name_index)

        _compile(compiler, code, method_sig)
        if nodes.is_empty_node(method_default_impl):
            _emit_void(code)
        else:
            _compile_case_function(compiler, code, node, nodes.empty_node(), method_default_impl)

        _emit_call(compiler, code, node, 4, lang_names.METHOD)
        # code.emit_1(METHOD, method_name_index, info(node))
        code.emit_2(STORE_LOCAL, method_index, method_name_index, info(node))
        if i != last_index:
            _emit_pop(code)


def _compile_IMPLEMENT(compiler, code, node):
    traitname = node_first(node)
    typename = node_second(node)
    methods = node_third(node)

    _compile_node_name_lookup(compiler, code, traitname)
    _compile_node_name_lookup(compiler, code, typename)

    len_methods = len(methods)
    for i, method in enumerate(methods):
        method_name = method[0]
        method_impl = method[1]
        _compile(compiler, code, method_name)
        # _compile_node_name_lookup(compiler, code, method_name)
        _compile_case_function(compiler, code, node,
                               nodes.empty_node(),
                               method_impl)
        code.emit_1(TUPLE, 2, info(method_name))

    code.emit_1(LIST, len_methods, info(traitname))

    # code.emit_0(IMPLEMENT, info(traitname))
    _emit_call(compiler, code, node, 3, lang_names.IMPLEMENT)


def _emit_TAIL(compiler, code, node):
    _compile(compiler, code, node)
    _emit_call(compiler, code, node, 1, lang_names.REST)


def _emit_HEAD(compiler, code, node):
    _compile(compiler, code, node)
    _emit_call(compiler, code, node, 1, lang_names.FIRST)


def _emit_DROP(compiler, code, node, drop):
    count = node_first(drop)
    _compile(compiler, code, count)
    _compile(compiler, code, node)
    _emit_call(compiler, code, node, 2, lang_names.DROP)


def _compile_LOOKUP(compiler, code, node):
    # TODO OPTIMISATION FOR INDEX LOOKUP
    obj = node_first(node)
    expr = node_second(node)
    # INTERNAL NODES GENERATED BY PATTERN COMPILER
    # WHICH USES STACK BASED  ALGORITHM FOR EVALUATING PATTERN PATH
    if node_type(expr) == NT_TAIL:
        return _emit_TAIL(compiler, code, obj)
    elif node_type(expr) == NT_HEAD:
        return _emit_HEAD(compiler, code, obj)
    elif node_type(expr) == NT_DROP:
        return _emit_DROP(compiler, code, obj, expr)

    _compile(compiler, code, expr)
    _compile(compiler, code, obj)
    _emit_call(compiler, code, node, 2, lang_names.AT)


def _compile_LOOKUP_SYMBOL(compiler, code, node):
    obj = node_first(node)
    _emit_symbol_literal(compiler, code, node_second(node))
    _compile(compiler, code, obj)
    _emit_call(compiler, code, node, 2, lang_names.AT)


def _compile_args_list(compiler, code, args):
    args_count = 0

    for arg in args:
        _compile(compiler, code, arg)
        args_count += 1

    return args_count


def _compile_CALL(compiler, code, node):
    func = node_first(node)
    args = node_second(node)

    # print "_compile_LPAREN", func, args

    arg_count = _compile_args_list(compiler, code, args)

    _compile(compiler, code, func)

    code.emit_1(CALL, arg_count, info(node))


######################################
##FIRST PASS
#######################################
####
# MAIN SWITCH
####

FIRST_PASS_FUNCS = [NT_FUN]
NEW_SCOPE_NODES = [NT_MODULE]


def _compile_1(compiler, code, ast):
    if is_empty_node(ast):
        return

    if nodes.is_list_node(ast):
        for node in ast:
            _compile_1(compiler, code, node)
    else:
        ntype = node_type(ast)
        # FIRST_PASS_FUNCS

        if ntype == NT_FUN:
            name = node_first(ast)
            if not is_empty_node(name):
                symbol = _get_symbol_name_or_empty(compiler.process, name)
                _declare_local(compiler, symbol)
                # _declare_function(compiler, code, name)
        else:
            return
            # NEW_SCOPE_NODES
            # elif ntype == NT_MODULE or ntype == NT_SPECIFY or nodes.node_arity(ast) == 0:
            #     return
            # else:
            #     children = nodes.node_children(ast)
            #     for node in children:
            #         _compile_1(compiler, code, node)


# compiler second_pass
def _compile(compiler, code, ast):
    if nodes.is_list_node(ast):
        _compile_nodes(compiler, code, ast)
    else:
        _compile_node(compiler, code, ast)


def _compile_2(compiler, code, ast):
    _compile_1(compiler, code, ast)
    _compile(compiler, code, ast)


def _compile_nodes(compiler, code, ast):
    # TODO MAKE ALL NODES HAS TYPE

    length = plist.length(ast)
    if length > 1:
        nodes_except_last = plist.slice(ast, 0, length - 1)
        for node in nodes_except_last:
            _compile(compiler, code, node)
            _emit_pop(code)

    if length > 0:
        last_node = plist.nth(ast, length - 1)
        _compile(compiler, code, last_node)


def _compile_node(compiler, code, node):
    ntype = node_type(node)

    if NT_TRUE == ntype:
        _compile_TRUE(compiler, code, node)
    elif NT_FALSE == ntype:
        _compile_FALSE(compiler, code, node)
    elif NT_FLOAT == ntype:
        _compile_FLOAT(compiler, code, node)
    elif NT_INT == ntype:
        _compile_INT(compiler, code, node)
    elif NT_STR == ntype:
        _compile_STR(compiler, code, node)
    elif NT_CHAR == ntype:
        _compile_CHAR(compiler, code, node)
    elif NT_NAME == ntype:
        _compile_NAME(compiler, code, node)
    elif NT_SYMBOL == ntype:
        _compile_SYMBOL(compiler, code, node)
    elif NT_TEMPORARY == ntype:
        _compile_TEMPORARY(compiler, code, node)

    elif NT_ASSIGN == ntype:
        _compile_ASSIGN(compiler, code, node)

    elif NT_FUN == ntype:
        _compile_FUN(compiler, code, node)

    elif NT_CONDITION == ntype:
        _compile_CONDITION(compiler, code, node)
    elif NT_TERNARY_CONDITION == ntype:
        _compile_WHEN(compiler, code, node)
    elif NT_WHEN == ntype:
        _compile_WHEN_NO_ELSE(compiler, code, node)
    elif NT_MATCH == ntype:
        _compile_MATCH(compiler, code, node)
    elif NT_TRY == ntype:
        _compile_TRY(compiler, code, node)
    elif NT_EXPORT == ntype:
        _compile_EXPORT(compiler, code, node)
    elif NT_IMPORT == ntype:
        _compile_IMPORT(compiler, code, node)
    elif NT_IMPORT_HIDING == ntype:
        _compile_IMPORT_HIDING(compiler, code, node)
    elif NT_IMPORT_FROM == ntype:
        _compile_IMPORT_FROM(compiler, code, node)
    elif NT_IMPORT_FROM_HIDING == ntype:
        _compile_IMPORT_FROM_HIDING(compiler, code, node)

    elif NT_MODULE == ntype:
        _compile_MODULE(compiler, code, node)
    elif NT_TRAIT == ntype:
        _compile_TRAIT(compiler, code, node)
    elif NT_IMPLEMENT == ntype:
        _compile_IMPLEMENT(compiler, code, node)
    elif NT_THROW == ntype:
        _compile_THROW(compiler, code, node)
    elif NT_CALL == ntype:
        _compile_CALL(compiler, code, node)

    elif NT_LIST == ntype:
        _compile_LIST(compiler, code, node)
    elif NT_TUPLE == ntype:
        _compile_TUPLE(compiler, code, node)
    elif NT_UNIT == ntype:
        _compile_UNIT(compiler, code, node)
    elif NT_MAP == ntype:
        _compile_MAP(compiler, code, node)

    elif NT_TYPE == ntype:
        _compile_TYPE(compiler, code, node)
    elif NT_UNION == ntype:
        _compile_UNION(compiler, code, node)
    elif NT_DERIVE == ntype:
        _compile_DERIVE(compiler, code, node)

    elif NT_LOOKUP == ntype:
        _compile_LOOKUP(compiler, code, node)
    elif NT_LOOKUP_SYMBOL == ntype:
        _compile_LOOKUP_SYMBOL(compiler, code, node)
    elif NT_IMPORTED_NAME == ntype:
        _compile_LOOKUP_MODULE(compiler, code, node)

    elif NT_MODIFY == ntype:
        _compile_MODIFY(compiler, code, node)
    elif NT_AND == ntype:
        _compile_AND(compiler, code, node)
    elif NT_OR == ntype:
        _compile_OR(compiler, code, node)
    elif NT_GOTO == ntype:
        _compile_GOTO(compiler, code, node)
    elif NT_UNDEFINE == ntype:
        _compile_UNDEFINE(compiler, code, node)
    elif NT_FENV == ntype:
        _compile_FENV(compiler, code, node)
    else:
        compile_error(compiler, code, node, u"Unknown node")


def newcode(compiler):
    return CodeSource(SourceInfo(compiler.source_path, compiler.source))


def compile_ast(compiler, ast, ast_scope):
    code = newcode(compiler)
    _enter_scope(compiler)
    _declare_arguments(compiler, 0, False)
    _compile_2(compiler, code, ast)
    scope = _current_scope(compiler)
    final_scope = scope.finalize(_previous_scope(compiler), ast_scope)
    _exit_scope(compiler)
    compiled_code = code.finalize_compilation(final_scope)
    return compiled_code


def compile(process, env, src, sourcename):
    ast, ast_scope = parser.parse(process, env, src)
    # print ast
    compiler = Compiler(process, env, sourcename, src)
    code = compile_ast(compiler, ast, ast_scope)
    return code


def compile_env(process, parent_env, modulename, src, sourcename):
    code = compile(process, parent_env, src, sourcename)
    module = space.newenvsource(modulename, code)
    return module


def compile_function_source(process, parent_env, src, name):
    code = compile(process, parent_env, src, name)
    fn = space.newfuncsource(name, code)
    return fn


def print_code(code):
    from code.opcode import opcode_to_str
    print "\n".join([str((opcode_to_str(c[0]), str(c[1:]))) for c in code.opcodes])

# CODE = compile(None, PATTERN_DATA)
# CODE = compile(None, """
#     A[1.._];
#     A[2..3];
#     A[_.._];
#     A[_..4];
#     A[5];
# """)
# print_code(CODE)
