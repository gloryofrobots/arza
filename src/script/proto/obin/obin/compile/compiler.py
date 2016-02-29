__author__ = 'gloryofrobots'
from obin.compile.code.opcode import *
from obin.compile.parse import parser
from obin.compile.parse import nodes
from obin.compile.parse.nodes import (node_type, node_arity,
                                      node_first, node_second, node_third, node_children, is_empty_node)
from obin.compile.parse.node_type import *
from obin.types import space, api, plist, environment, symbol as symbols
from obin.compile.code.source import CodeSource, codeinfo, codeinfo_unknown, SourceInfo
from obin.misc import platform, strutil
from obin.runtime import error


# TODO REMOVE NIL as token and node_type

def compile_error(compiler, code, node, message):
    line = code.info.get_line(api.to_i(nodes.node_line(node)))
    return error.throw(error.Errors.COMPILE,
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


# TODO GET RID OF
def _emit_fself(compiler, code, node, name):
    code.emit_0(FSELF, info(node))
    _emit_store(compiler, code, name, node)


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
    if space.isnil(ref):
        return compile_error(compiler, code, node, u"Unreachable variable")

    _declare_static_reference(compiler, ref)

    return ref_id, False


"""
    HOOKS
"""


def _compile_FLOAT(compiler, code, node):
    value = float(nodes.node_value_s(node))
    idx = _declare_literal(compiler, space.newfloat(value))
    code.emit_1(LITERAL, idx, info(node))


def _compile_INT(compiler, code, node):
    value = strutil.string_to_int(nodes.node_value_s(node))
    idx = _declare_literal(compiler, space.newnumber(value))
    code.emit_1(LITERAL, idx, info(node))


def _emit_integer(compiler, code, integer):
    idx = _declare_literal(compiler, space.newint(integer))
    code.emit_1(LITERAL, idx, codeinfo_unknown())


def _compile_TRUE(compiler, code, node):
    code.emit_0(TRUE, info(node))


def _compile_FALSE(compiler, code, node):
    code.emit_0(FALSE, info(node))


def _compile_NIL(compiler, code, node):
    code.emit_0(NIL, info(node))


def _get_symbol_or_name_value(name):
    ntype = node_type(name)
    if ntype == NT_SYMBOL:
        return _get_name_value(node_first(name))
    elif ntype == NT_LOOKUP_MODULE:
        return _module_path_to_string(name)
    else:
        return _get_name_value(name)


def _get_name_value(name):
    ntype = node_type(name)
    if ntype == NT_SYMBOL:
        return _get_name_value(node_first(name))
    elif ntype == NT_STR:
        value = _get_special_name_value(name)
    elif ntype == NT_NAME:
        value = nodes.node_value_s(name)
    else:
        assert False, ("_get_name_value", ntype)
    return value


def _get_symbol_name(compiler, name):
    sym = _get_symbol_or_name_value(name)
    return space.newsymbol_s(compiler.process, sym)


def _emit_pop(code):
    code.emit_0(POP, codeinfo_unknown())


def _emit_dup(code):
    code.emit_0(DUP, codeinfo_unknown())


def _emit_nil(code):
    code.emit_0(NIL, codeinfo_unknown())

def _emit_empty_list(code):
    code.emit_1(LIST, 0, codeinfo_unknown())

def _emit_literal(compiler, code, node, literal):
    idx = _declare_literal(compiler, literal)
    code.emit_1(LITERAL, idx, info(node))


def _emit_symbol_name(compiler, code, name):
    symbol = _get_symbol_name(compiler, name)
    _emit_literal(compiler, code, name, symbol)


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


def _compile_ASSIGN_MEMBER(compiler, code, node):
    member = node_first(node)
    value = node_second(node)
    obj = node_first(member)
    item = node_second(member)

    _compile(compiler, code, obj)
    _compile(compiler, code, item)
    _compile(compiler, code, value)
    code.emit_0(STORE_MEMBER, info(node))


def _compile_ASSIGN_SYMBOL(compiler, code, node):
    member = node_first(node)

    obj = node_first(member)
    _compile(compiler, code, obj)
    _emit_symbol_name(compiler, code, node_second(member))
    _compile(compiler, code, node_second(node))
    code.emit_0(STORE_MEMBER, info(node))


def _emit_store_name(compiler, code, namenode):
    name = space.newsymbol_s(compiler.process, nodes.node_value_s(namenode))
    _emit_store(compiler, code, name, namenode)


def _emit_store(compiler, code, name, namenode):
    index = _declare_local(compiler, name)

    name_index = _declare_literal(compiler, name)
    code.emit_2(STORE_LOCAL, index, name_index, info(namenode))


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
    from obin.compile import MATCH_SYS_VAR
    name = space.newsymbol_s(compiler.process, MATCH_SYS_VAR)
    name_index = _declare_literal(compiler, name)
    index = _declare_local(compiler, name)
    code.emit_2(STORE_LOCAL, index, name_index, codeinfo_unknown())

    endmatch = code.prealocate_label()
    graph = transform(compiler, code, node, patterns, create_goto_node(endmatch))
    _compile(compiler, code, graph)

    # Allocate error in case of no match
    err_node = nodes.create_match_fail_node(node, str(error_code), MATCH_SYS_VAR)
    _compile(compiler, code, err_node)
    code.emit_0(THROW, info(node))

    code.emit_1(LABEL, endmatch, codeinfo_unknown())


def _compile_MATCH(compiler, code, node):
    exp = node_first(node)
    patterns = node_second(node)
    _compile(compiler, code, exp)
    _compile_match(compiler, code, node, patterns, error.Errors.MATCH)


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
# DESTRUCT DESTRUCT
####
def _compile_destruct(compiler, code, node):
    _compile(compiler, code, node_second(node))
    return _compile_destruct_recur(compiler, code, node_first(node))


def _is_optimizable_unpack_seq_pattern(node):
    items = node_first(node)
    for child in items:
        if child is None:
            print ""
        if node_type(child) != NT_NAME:
            return False
    return True


def _compile_destruct_recur(compiler, code, node):
    if node_type(node) == NT_TUPLE:
        # x,y,z = foo() optimisation to single unpack opcode
        if _is_optimizable_unpack_seq_pattern(node):
            return _compile_destruct_unpack_seq(compiler, code, node)
        else:
            return _compile_destruct_recur_seq(compiler, code, node)
    elif node_type(node) == NT_MAP:
        return _compile_destruct_recur_map(compiler, code, node)
    else:
        compile_error(compiler, code, node, u"unsupported assignment syntax")


def _compile_destruct_recur_map(compiler, code, node):
    pairs = node_first(node)
    for pair in pairs:
        _emit_dup(code)

        key = pair[0]
        value = pair[1]
        varname = None
        if is_empty_node(value):
            varname = key
        elif node_type(value) == NT_NAME:
            varname = value

        _emit_map_key(compiler, code, key)

        code.emit_0(MEMBER, info(key))

        if varname is None:
            _compile_destruct_recur(compiler, code, value)
            _emit_pop(code)
        else:
            _emit_store_name(compiler, code, varname)
            _emit_pop(code)


##################################################
# DESTRUCT SEQUENCE
##################################################

def _compile_destruct_recur_seq_rest(compiler, code, last_item, last_index):
    _emit_dup(code)
    varname = node_first(last_item)
    _emit_integer(compiler, code, last_index)
    _emit_nil(code)
    code.emit_0(SLICE, codeinfo_unknown())
    _emit_store_name(compiler, code, varname)
    _emit_pop(code)


def _compile_destruct_recur_seq_item(compiler, code, item, index):
    _emit_dup(code)

    varname = None
    if node_type(item) == NT_NAME:
        varname = item

    idx = _declare_literal(compiler, space.newint(index))
    code.emit_1(LITERAL, idx, info(item))
    code.emit_0(MEMBER, info(item))

    if varname is None:
        _compile_destruct_recur(compiler, code, item)
        _emit_pop(code)
    else:
        _emit_store_name(compiler, code, varname)
        _emit_pop(code)


def _compile_destruct_recur_seq(compiler, code, node):
    items = node_first(node)
    length = len(items)

    last_index = length - 1

    for i in range(last_index):
        item = items[i]
        _compile_destruct_recur_seq_item(compiler, code, item, i)

    last_item = items[last_index]
    if node_type(last_item) == NT_REST:
        _compile_destruct_recur_seq_rest(compiler, code, last_item, last_index)
    else:
        _compile_destruct_recur_seq_item(compiler, code, last_item, last_index)


def _compile_destruct_unpack_seq(compiler, code, node):
    _emit_dup(code)
    names = node_first(node)
    length = len(names)
    code.emit_1(UNPACK_SEQUENCE, length, info(node))
    # TODO FIX IT
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
    if node_type(left) == NT_LOOKUP_SYMBOL:
        return _compile_ASSIGN_SYMBOL(compiler, code, node)
    elif node_type(left) == NT_LOOKUP:
        return _compile_ASSIGN_MEMBER(compiler, code, node)
    elif node_type(left) == NT_TUPLE or node_type(left) == NT_MAP:
        return _compile_destruct(compiler, code, node)

    _compile(compiler, code, node_second(node))
    _emit_store_name(compiler, code, left)


def _compile_node_name_lookup(compiler, code, node):
    name = _get_symbol_name(compiler, node)

    index, is_local = _get_variable_index(compiler, code, node, name)
    name_index = _declare_literal(compiler, name)
    if is_local:
        code.emit_2(LOCAL, index, name_index, info(node))
    else:
        code.emit_2(OUTER, index, name_index, info(node))


def _get_special_name_value(node):
    # REMOVE BACKTICKS `xxx`
    return nodes.node_value_s(node)[1:len(nodes.node_value_s(node)) - 1]


def _compile_NAME(compiler, code, node):
    _compile_node_name_lookup(compiler, code, node)


def _compile_SYMBOL(compiler, code, node):
    name = node_first(node)
    _emit_symbol_name(compiler, code, name)


def _compile_RETURN(compiler, code, node):
    expr = node_first(node)
    _compile(compiler, code, expr)

    code.emit_0(RETURN, info(node))


def _compile_THROW(compiler, code, node):
    expr = node_first(node)
    _compile(compiler, code, expr)
    code.emit_0(THROW, info(node))


# TODO MAKE NAMES from SYMBOLS in parser
def _emit_map_key(compiler, code, key):
    if node_type(key) == NT_NAME:
        # in case of names in object literal we must convert them to symbols
        _emit_symbol_name(compiler, code, key)
    else:
        _compile(compiler, code, key)


def _compile_MODIFY(compiler, code, node):
    obj = node_first(node)
    modifications = node_second(node)
    _compile(compiler, code, obj)

    for m in modifications:
        key = m[0]
        value = m[1]
        _emit_map_key(compiler, code, key)
        _compile(compiler, code, value)
        code.emit_0(STORE_MEMBER, info(key))


def _compile_MAP(compiler, code, node):
    items = node_first(node)
    for c in items:
        key = c[0]
        value = c[1]
        if is_empty_node(value):
            _compile_NIL(compiler, code, value)
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


# def _emit_list(compiler, code, node):
#     items = node_first(node)
#
#     for c in items:
#         _compile(compiler, code, c)
#
#     code.emit_1(LIST, len(items))


def _compile_BREAK(compiler, code, node):
    _emit_nil(code)
    if not code.emit_break():
        compile_error(compiler, code, node, u"break outside loop")


def _compile_CONTINUE(compiler, code, node):
    _emit_nil(code)
    if not code.emit_continue():
        compile_error(compiler, code, node, u"continue outside loop")


def _compile_func_args_and_body(compiler, code, name, params, body):
    funcname = _get_symbol_name_or_empty(compiler.process, name)
    _enter_scope(compiler)

    funccode = newcode(compiler)

    if node_type(params) == NT_UNIT:
        _declare_arguments(compiler, 0, False)
    else:
        args = node_first(params)
        length = len(args)
        funccode.emit_0(ARGUMENTS, codeinfo_unknown())

        last_param = args[length - 1]
        is_variadic = True if node_type(last_param) == NT_REST else False
        _declare_arguments(compiler, length, is_variadic)
        _compile_destruct_recur(compiler, funccode, params)

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

    funccode.emit_0(ARGUMENTS, codeinfo_unknown())
    _compile_match(compiler, funccode, node, cases, error.Errors.FUNCTION_MATCH)
    current_scope = _current_scope(compiler)
    scope = current_scope.finalize(_previous_scope(compiler), None)
    _exit_scope(compiler)

    compiled_code = funccode.finalize_compilation(scope)

    source = space.newfuncsource(funcname, compiled_code)
    source_index = _declare_literal(compiler, source)
    code.emit_1(FUNCTION, source_index, info(node))


def _get_symbol_name_or_empty(process, name):
    if is_empty_node(name):
        return space.newsymbol(process, u"")
    else:
        return space.newsymbol_s(process, nodes.node_value_s(name))


def is_simple_func_declaration(params):
    ntype = node_type(params)
    if ntype == NT_TUPLE:
        for child in node_first(params):
            child_type = node_type(child)
            if child_type == NT_MAP:
                if not is_simple_func_declaration(child):
                    return False
            elif node_type(child) not in [NT_REST, NT_NAME]:
                # print "node_type(child) not in [NT_REST, NT_NAME]:", node_type(child)
                return False
        return True
    elif ntype == NT_MAP:
        for child in node_first(params):
            if node_type(child[0]) != NT_NAME:
                # print "node_type(child[0]) != NT_NAME:"
                return False
            if not is_empty_node(child[1]):
                # print "not is_empty_node(child[1]): "
                return False
        return True
    elif ntype == NT_UNIT:
        return True
    # print "NOT SIMPLE ", ntype
    return False


def _compile_DEF(compiler, code, node):
    namenode = node_first(node)
    funcname = _get_symbol_name_or_empty(compiler.process, namenode)

    funcs = node_second(node)
    # single function
    if len(funcs) == 1:
        func = funcs[0]
        params = func[0]
        body = func[1]
        if not is_simple_func_declaration(params):
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
    _emit_nil(code)
    code.emit_1(LABEL, endif, codeinfo_unknown())


def _compile_IF(compiler, code, node):
    branches = node_first(node)

    endif = code.prealocate_label()
    length = len(branches)
    for i in range(length - 1):
        branch = branches[i]
        _compile_branch(compiler, code, branch[0], branch[1], endif)

    elsebranch = branches[length - 1]
    if is_empty_node(elsebranch):
        _emit_nil(code)
    else:
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
    _compile_match(compiler, code, node, catches, error.Errors.EXCEPTION_MATCH)

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
    if node_type(node) == NT_LOOKUP_MODULE:
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
    elif node_type(exp) == NT_LOOKUP_MODULE:
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


def _emit_imported(compiler, code, node, module, var_name, bind_name):
    func = api.at(module, var_name)
    idx = _declare_import(compiler, bind_name, func)
    code.emit_1(IMPORTED, idx, info(node))
    _emit_store(compiler, code, bind_name, node)


def _compile_IMPORT(compiler, code, node):
    colon = space.newsymbol(compiler.process, u":")
    module, import_name, var_names = _get_import_data_and_emit_module(compiler, code, node)
    for var_name, bind_name in var_names:
        full_bind_name = symbols.concat_3(compiler.process, import_name, colon, bind_name)
        _emit_imported(compiler, code, node, module, var_name, full_bind_name)


def _compile_IMPORT_FROM(compiler, code, node):
    module, import_name, var_names = _get_import_data_and_emit_module(compiler, code, node)
    for var_name, bind_name in var_names:
        _emit_imported(compiler, code, node, module, var_name, bind_name)


def _delete_hiding_names(compiler, code, node, module, var_names):
    exports = module.exports()
    imported = []
    for var_name, bind_name in var_names:
        if var_name in exports:
            continue
        imported.append(var_name)
    return imported


def _compile_IMPORT_HIDING(compiler, code, node):
    colon = space.newsymbol(compiler.process, u":")
    module, import_name, var_names = _get_import_data_and_emit_module(compiler, code, node)
    var_names = _delete_hiding_names(compiler, code, node, module, var_names)
    for var_name in var_names:
        bind_name = symbols.concat_3(compiler.process, import_name, colon, var_name)
        _emit_imported(compiler, code, node, module, var_name, bind_name)


def _compile_IMPORT_FROM_HIDING(compiler, code, node):
    colon = space.newsymbol(compiler.process, u":")
    module, import_name, var_names = _get_import_data_and_emit_module(compiler, code, node)
    var_names = _delete_hiding_names(compiler, code, node, module, var_names)
    for var_name in var_names:
        _emit_imported(compiler, code, node, module, var_name, var_name)


def _compile_MODULE(compiler, code, node):
    name_node = node_first(node)
    body = node_second(node)
    parse_scope = node_third(node)

    compiled_code = compile_ast(compiler, body, parse_scope)

    module_name = _get_symbol_name(compiler, name_node)
    module = space.newenvsource(module_name, compiled_code)
    module_index = _declare_literal(compiler, module)
    code.emit_1(MODULE, module_index, info(node))

    _emit_store(compiler, code, module_name, name_node)


def _compile_GENERIC(compiler, code, node):
    name_node = node_first(node)
    name = _get_symbol_name(compiler, name_node)

    name_index = _declare_literal(compiler, name)
    # index = _get_function_index(compiler, name)
    index = _declare_local(compiler, name)
    code.emit_1(GENERIC, name_index, info(node))
    code.emit_2(STORE_LOCAL, index, name_index, info(name_node))

    if node_arity(node) == 2:
        methods = node_second(node)
        _emit_specify(compiler, code, node, methods)


def _compile_TYPE(compiler, code, node):
    name_node = node_first(node)
    name = _get_symbol_name(compiler, name_node)

    name_index = _declare_literal(compiler, name)
    index = _declare_local(compiler, name)

    constructor = node_third(node)
    fields = node_second(node)

    _emit_nil(code)
    if is_empty_node(fields):
        _emit_empty_list(code)
        _emit_nil(code)
    else:
        _compile(compiler, code, fields)
        _compile_case_function(compiler, code, node, nodes.empty_node(), constructor)

    code.emit_1(TYPE, name_index, info(node))
    code.emit_2(STORE_LOCAL, index, name_index, info(name_node))


def _compile_FENV(compiler, code, node):
    code.emit_0(FENV, info(node))


def _compile_TRAIT(compiler, code, node):
    names = node_first(node)
    for name in names:
        name = space.newsymbol_s(compiler.process, nodes.node_value_s(name))
        index = _declare_local(compiler, name)

        name_index = _declare_literal(compiler, name)
        code.emit_1(TRAIT, name_index, info(node))
        code.emit_2(STORE_LOCAL, index, name_index, info(node))


def _emit_specify(compiler, code, node, methods):
    for method in methods:
        method_args = method[0]
        method_body = method[1]
        args = []
        signature = []
        for arg in method_args:
            if node_type(arg) == NT_OF:
                args.append(node_first(arg))
                signature.append(node_second(arg))
            else:
                args.append(arg)
                signature.append(None)

        for trait in signature:
            if trait is None:
                _emit_nil(code)
            else:
                _compile(compiler, code, trait)

        code.emit_1(TUPLE, len(signature), info(node))

        args_node = nodes.create_tuple_node(node, args)
        _compile_func_args_and_body(compiler, code, nodes.empty_node(), args_node,
                                    method_body)
        code.emit_1(TUPLE, 2, info(node))

    code.emit_1(SPECIFY, len(methods), info(node))


def _compile_SPECIFY(compiler, code, node):
    name = node_first(node)
    _compile(compiler, code, name)
    methods = node_second(node)
    _emit_specify(compiler, code, node, methods)


def _compile_FOR(compiler, code, node):
    source = node_second(node)
    body = node_third(node)
    _compile(compiler, code, source)
    code.emit_0(ITERATOR, info(node))
    # load the "last" iterations result
    _emit_nil(code)
    precond = code.emit_startloop_label()
    code.continue_at_label(precond)
    finish = code.prealocate_endloop_label(False)
    # update = code.prealocate_updateloop_label()

    code.emit_1(JUMP_IF_ITERATOR_EMPTY, finish, codeinfo_unknown())

    # put next iterator value on stack
    code.emit_0(NEXT, codeinfo_unknown())

    vars = node_first(node)
    name = space.newsymbol_s(compiler.process, nodes.node_value_s(vars[0]))
    index = _declare_local(compiler, name)

    name_index = _declare_literal(compiler, name)
    code.emit_2(STORE_LOCAL, index, name_index, info(node))
    _emit_pop(code)

    _compile(compiler, code, body)
    # code.emit_updateloop_label(update)

    code.emit_1(JUMP, precond, codeinfo_unknown())
    code.emit_endloop_label(finish)


def _compile_WHILE(compiler, code, node):
    condition = node_first(node)
    body = node_second(node)
    _emit_nil(code)
    startlabel = code.emit_startloop_label()
    code.continue_at_label(startlabel)
    _compile(compiler, code, condition)
    endlabel = code.prealocate_endloop_label()
    code.emit_1(JUMP_IF_FALSE, endlabel, codeinfo_unknown())
    _emit_pop(code)
    _compile(compiler, code, body)
    code.emit_1(JUMP, startlabel, codeinfo_unknown())
    code.emit_endloop_label(endlabel)
    code.done_continue()


def _compile_LOOKUP_SYMBOL(compiler, code, node):
    obj = node_first(node)
    _compile(compiler, code, obj)
    _emit_symbol_name(compiler, code, node_second(node))
    code.emit_0(MEMBER, info(node))


def _emit_SLICE(compiler, code, obj, slice):
    start = node_first(slice)
    end = node_second(slice)

    _compile(compiler, code, obj)

    if nodes.is_wildcard_node(start):
        _emit_nil(code)
    else:
        _compile(compiler, code, start)

    if nodes.is_wildcard_node(end):
        _emit_nil(code)
    else:
        _compile(compiler, code, end)

    code.emit_0(SLICE, info(slice))


def _compile_LOOKUP(compiler, code, node):
    # TODO OPTIMISATION FOR INDEX LOOKUP
    obj = node_first(node)
    expr = node_second(node)
    if node_type(expr) == NT_RANGE:
        return _emit_SLICE(compiler, code, obj, expr)

    _compile(compiler, code, obj)
    _compile(compiler, code, expr)
    code.emit_0(MEMBER, info(node))


def _compile_args_list(compiler, code, args):
    args_count = 0

    for arg in args:
        _compile(compiler, code, arg)
        args_count += 1

    return args_count


def _compile_CALL_MEMBER(compiler, code, node):
    obj = node_first(node)
    method = node_second(node)
    args = node_third(node)
    # print "_compile_LPAREN_MEMBER", obj, method, args

    args_count = _compile_args_list(compiler, code, args)

    _compile(compiler, code, obj)
    _emit_symbol_name(compiler, code, method)
    # TODO LITERAL HERE
    # declare_symbol(compiler.process, compiler,name)

    code.emit_1(CALL_METHOD, args_count, info(node))


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

FIRST_PASS_FUNCS = [NT_FUN, NT_GENERIC]
NEW_SCOPE_NODES = [NT_MODULE, NT_SPECIFY]


def _compile_1(compiler, code, ast):
    if is_empty_node(ast):
        return

    if nodes.is_list_node(ast):
        for node in ast:
            _compile_1(compiler, code, node)
    else:
        ntype = node_type(ast)
        # FIRST_PASS_FUNCS

        if ntype == NT_FUN or ntype == NT_GENERIC:
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
    elif NT_NIL == ntype:
        _compile_NIL(compiler, code, node)
    elif NT_INT == ntype:
        _compile_INT(compiler, code, node)
    elif NT_FLOAT == ntype:
        _compile_FLOAT(compiler, code, node)
    elif NT_STR == ntype:
        _compile_STR(compiler, code, node)
    elif NT_CHAR == ntype:
        _compile_CHAR(compiler, code, node)
    elif NT_NAME == ntype:
        _compile_NAME(compiler, code, node)
    elif NT_SYMBOL == ntype:
        _compile_SYMBOL(compiler, code, node)

    elif NT_ASSIGN == ntype:
        _compile_ASSIGN(compiler, code, node)

    elif NT_FUN == ntype:
        _compile_DEF(compiler, code, node)

    elif NT_CONDITION == ntype:
        _compile_IF(compiler, code, node)
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
    elif NT_GENERIC == ntype:
        _compile_GENERIC(compiler, code, node)
    elif NT_SPECIFY == ntype:
        _compile_SPECIFY(compiler, code, node)

    elif NT_RETURN == ntype:
        _compile_RETURN(compiler, code, node)
    elif NT_THROW == ntype:
        _compile_THROW(compiler, code, node)

    elif NT_BREAK == ntype:
        _compile_BREAK(compiler, code, node)
    elif NT_CONTINUE == ntype:
        _compile_CONTINUE(compiler, code, node)
    elif NT_FOR == ntype:
        _compile_FOR(compiler, code, node)
    elif NT_WHILE == ntype:
        _compile_WHILE(compiler, code, node)

    elif NT_CALL == ntype:
        _compile_CALL(compiler, code, node)
    elif NT_CALL_MEMBER == ntype:
        _compile_CALL_MEMBER(compiler, code, node)

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

    elif NT_LOOKUP == ntype:
        _compile_LOOKUP(compiler, code, node)
    elif NT_LOOKUP_SYMBOL == ntype:
        _compile_LOOKUP_SYMBOL(compiler, code, node)
    elif NT_LOOKUP_MODULE == ntype:
        _compile_LOOKUP_MODULE(compiler, code, node)

    elif NT_MODIFY == ntype:
        _compile_MODIFY(compiler, code, node)
    elif NT_AND == ntype:
        _compile_AND(compiler, code, node)
    elif NT_OR == ntype:
        _compile_OR(compiler, code, node)
    elif NT_GOTO == ntype:
        _compile_GOTO(compiler, code, node)
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
