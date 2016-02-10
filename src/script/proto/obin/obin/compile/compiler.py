__author__ = 'gloryofrobots'
from obin.compile.code.opcode import *
from obin.compile.parse import parser
from obin.compile.parse import nodes
from obin.compile.parse.nodes import (node_type, node_arity,
                                      node_first, node_second, node_third, node_children)
from obin.compile.parse.node_type import *
from obin.compile.compile_scope import Scope
from obin.types import space, api, plist
from obin.builtins.internals import internals
from obin.compile.code.source import CodeSource, codeinfo, codeinfo_unknown, SourceInfo
from obin.misc import platform, strutil
from obin.runtime import error


# TODO REMOVE NIL IN ELSE FROM IF. ADD IF_NO_ELSE NODE_TYPE FOR PATTERN MATCHING
# TODO REMOVE NIL as token and node_type

def compile_error(compiler, code, node, message):
    line = code.info.get_line(api.to_i(nodes.node_line(node)))
    return error.throw(error.Errors.COMPILE,
                       space.newtuple([
                           space.newstring(message),
                           space.newint(nodes.node_type(node)),
                           space.newstring_from_str(nodes.node_value(node)),
                           space.newtuple([space.newstring(u"line"), nodes.node_line(node),
                                           space.newstring(u"column"), nodes.node_column(node)]),
                           space.newstring(line)
                       ]))


class Compiler:
    def __init__(self, process, path, src):
        self.process = process
        self.scopes = []
        self.depth = -1
        self.source_path = path
        self.source = src


def info(node):
    if nodes.is_empty_node(node):
        return codeinfo_unknown()
    return codeinfo(nodes.node_position(node), nodes.node_line(node), nodes.node_column(node))


########################
# SCOPES
########################


def _enter_scope(compiler):
    compiler.depth += 1

    new_scope = Scope()
    compiler.scopes.append(new_scope)
    # print 'starting new scope %d' % (compiler.process, compiler.depth, )


def _is_modifiable_binding(compiler, name):
    scope = _current_scope(compiler)
    if not platform.is_absent_index(scope.get_scope_local_index(name)):
        return True

    return False


def _declare_arguments(compiler, args_count, varargs):
    _current_scope(compiler).declare_scope_arguments(args_count, varargs)


def _declare_function_name(compiler, name):
    _current_scope(compiler).add_scope_function_name(name)


def _declare_reference(compiler, symbol):
    assert space.issymbol(symbol)
    scope = _current_scope(compiler)
    idx = scope.get_scope_reference(symbol)
    if platform.is_absent_index(idx):
        idx = scope.add_scope_reference(symbol)
    return idx


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


def _get_variable_index(compiler, name):
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

    # compile_error(process,process, compiler.current_node, "Non reachable variable", name)
    # COMMENT ERROR BECAUSE OF LATER LINKING OF BUILTINS
    ref_id = _declare_reference(compiler, name)
    return ref_id, False


def _exit_scope(compiler):
    compiler.depth = compiler.depth - 1
    compiler.scopes.pop()
    # print 'closing scope, returning to %d' % (process, compiler.depth, )


def _current_scope(compiler):
    return compiler.scopes[-1]


"""
    HOOKS
"""


def _compile_FLOAT(compiler, code, node):
    value = float(nodes.node_value(node))
    idx = _declare_literal(compiler, space.newfloat(value))
    code.emit_1(LITERAL, idx, info(node))


def _compile_INT(compiler, code, node):
    value = int(nodes.node_value(node))
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


def _get_name_value(name):
    ntype = node_type(name)
    if ntype == NT_SPECIAL_NAME:
        value = _get_special_name_value(name)
    elif ntype == NT_NAME:
        value = nodes.node_value(name)
    else:
        assert False, ("_get_name_value", ntype)
    return value


def _emit_pop(code):
    code.emit_0(POP, codeinfo_unknown())


def _emit_dup(code):
    code.emit_0(DUP, codeinfo_unknown())


def _emit_nil(code):
    code.emit_0(NIL, codeinfo_unknown())


def _emit_symbol_name(compiler, code, name):
    value = _get_name_value(name)
    symbol = space.newsymbol_py_str(compiler.process, value)
    idx = _declare_literal(compiler, symbol)
    code.emit_1(LITERAL, idx, info(name))


def _compile_STR(compiler, code, node):
    from obin.runistr import unicode_unescape, decode_str_utf8

    try:
        strval = str(nodes.node_value(node))
        strval = decode_str_utf8(strval)
        strval = strutil.string_unquote(strval)
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
        strval = str(nodes.node_value(node))
        strval = decode_str_utf8(strval)
        strval = strutil.string_unquote(strval)
        strval = unicode_unescape(strval)
        string = space.newstring(strval)
        idx = _declare_literal(compiler, string)
        code.emit_1(LITERAL, idx, info(node))
    except RuntimeError as e:
        compile_error(compiler, code, node, unicode(e.args[0]))



def _on_binary_primitive(compiler, code, node, name):
    _compile(compiler, code, node_first(node))
    _compile(compiler, code, node_second(node))
    code.emit_1(CALL_INTERNAL, name, info(node))


def _on_unary_primitive(compiler, code, node, name):
    _compile(compiler, code, node_first(node))
    code.emit_1(CALL_INTERNAL, name, info(node))


def _compile_BITAND(compiler, code, node):
    _on_binary_primitive(compiler, code, node, internals.BITAND)


def _compile_BITOR(compiler, code, node):
    _on_binary_primitive(compiler, code, node, internals.BITOR)


def _compile_BITXOR(compiler, code, node):
    _on_binary_primitive(compiler, code, node, internals.BITXOR)


def _compile_UNARY_PLUS(compiler, code, node):
    _on_unary_primitive(compiler, code, node, internals.UPLUS)


def _compile_ADD(compiler, code, node):
    _on_binary_primitive(compiler, code, node, internals.ADD)


def _compile_MUL(compiler, code, node):
    _on_binary_primitive(compiler, code, node, internals.MUL)


def _compile_MOD(compiler, code, node):
    _on_binary_primitive(compiler, code, node, internals.MOD)


def _compile_DIV(compiler, code, node):
    _on_binary_primitive(compiler, code, node, internals.DIV)


def _compile_UNARY_MINUS(compiler, code, node):
    _on_unary_primitive(compiler, code, node, internals.UMINUS)


def _compile_SUB(compiler, code, node):
    _on_binary_primitive(compiler, code, node, internals.SUB)


def _compile_BITNOT(compiler, code, node):
    _on_unary_primitive(compiler, code, node, internals.BITNOT)


def _compile_NOT(compiler, code, node):
    _on_unary_primitive(compiler, code, node, internals.NOT)


def _compile_GE(compiler, code, node):
    _on_binary_primitive(compiler, code, node, internals.GE)


def _compile_GT(compiler, code, node):
    _on_binary_primitive(compiler, code, node, internals.GT)


def _compile_LE(compiler, code, node):
    _on_binary_primitive(compiler, code, node, internals.LE)


def _compile_LT(compiler, code, node):
    _on_binary_primitive(compiler, code, node, internals.LT)


def _compile_IS(compiler, code, node):
    _on_binary_primitive(compiler, code, node, internals.IS)


def _compile_ISNOT(compiler, code, node):
    _on_binary_primitive(compiler, code, node, internals.ISNOT)


def _compile_ISA(compiler, code, node):
    _on_binary_primitive(compiler, code, node, internals.ISA)


def _compile_NOTA(compiler, code, node):
    _on_binary_primitive(compiler, code, node, internals.NOTA)


def _compile_KINDOF(compiler, code, node):
    _on_binary_primitive(compiler, code, node, internals.KINDOF)


def _compile_IN(compiler, code, node):
    _on_binary_primitive(compiler, code, node, internals.IN)


def _compile_NOTIN(compiler, code, node):
    _on_binary_primitive(compiler, code, node, internals.NOTIN)


def _compile_EQ(compiler, code, node):
    _on_binary_primitive(compiler, code, node, internals.EQ)


def _compile_NE(compiler, code, node):
    _on_binary_primitive(compiler, code, node, internals.NE)


def _compile_LSHIFT(compiler, code, node):
    _on_binary_primitive(compiler, code, node, internals.LSH)


def _compile_RSHIFT(compiler, code, node):
    _on_binary_primitive(compiler, code, node, internals.RSH)


def _compile_URSHIFT(compiler, code, node):
    _on_binary_primitive(compiler, code, node, internals.URSH)


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
    name = space.newsymbol_py_str(compiler.process, nodes.node_value(namenode))
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
    name = space.newsymbol_py_str(compiler.process, MATCH_SYS_VAR)
    name_index = _declare_literal(compiler, name)
    index = _declare_local(compiler, name)
    code.emit_2(STORE_LOCAL, index, name_index, codeinfo_unknown())

    endmatch = code.prealocate_label()
    graph = transform(compiler, code, node, patterns, create_goto_node(endmatch))
    _compile(compiler, code, graph)

    # Allocate error in case of no match
    err_node = nodes.create_match_fail_node(node, str(error_code))
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

    value = int(nodes.node_value(node))
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
        if nodes.is_empty_node(value):
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
    name_value = _get_name_value(node)
    name = space.newsymbol_py_str(compiler.process, name_value)

    index, is_local = _get_variable_index(compiler, name)
    name_index = _declare_literal(compiler, name)
    if is_local:
        code.emit_2(LOCAL, index, name_index, info(node))
    else:
        code.emit_2(OUTER, index, name_index, info(node))


def _get_special_name_value(node):
    # REMOVE BACKTICKS `xxx`
    return nodes.node_value(node)[1:len(nodes.node_value(node)) - 1]


def _compile_SPECIAL_NAME(compiler, code, node):
    _compile_node_name_lookup(compiler, code, node)


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
        if nodes.is_empty_node(value):
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
        _declare_function_name(compiler, funcname)

    _compile(compiler, funccode, body)
    current_scope = _current_scope(compiler)
    scope = current_scope.finalize()
    _exit_scope(compiler)
    # print "LOCALS:", str(scope.variables.keys())
    # print "REFS:", str(scope.references)
    compiled_code = funccode.finalize_compilation(scope)
    # print [str(c) for c in compiled_code.opcodes]
    # print "-------------------------"

    source = space.newfuncsource(funcname, compiled_code)
    source_index = _declare_literal(compiler, source)
    code.emit_1(FUNCTION, source_index, info(name))


def _compile_case_function(compiler, code, node, funcname, cases):
    _enter_scope(compiler)

    funccode = newcode(compiler)

    _declare_arguments(compiler, 0, True)

    if not api.isempty(funcname):
        _declare_function_name(compiler, funcname)

    funccode.emit_0(ARGUMENTS, codeinfo_unknown())

    _compile_match(compiler, funccode, node, cases, error.Errors.FUNCTION_MATCH)
    current_scope = _current_scope(compiler)
    scope = current_scope.finalize()
    _exit_scope(compiler)

    compiled_code = funccode.finalize_compilation(scope)

    source = space.newfuncsource(funcname, compiled_code)
    source_index = _declare_literal(compiler, source)
    code.emit_1(FUNCTION, source_index, info(node))


def _get_symbol_name_or_empty(process, name):
    if nodes.is_empty_node(name):
        return space.newsymbol(process, u"")
    else:
        return space.newsymbol_py_str(process, nodes.node_value(name))


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
            if not nodes.is_empty_node(child[1]):
                # print "not nodes.is_empty_node(child[1]): "
                return False
        return True
    elif ntype == NT_UNIT:
        return True
    # print "NOT SIMPLE ", ntype
    return False


def _compile_DEF(compiler, code, node):
    name = node_first(node)
    funcname = _get_symbol_name_or_empty(compiler.process, name)

    funcs = node_second(node)
    # single function
    if len(funcs) == 1:
        func = funcs[0]
        params = func[0]
        body = func[1]
        if not is_simple_func_declaration(params):
            _compile_case_function(compiler, code, node, funcname, funcs)
        else:
            # print "SIMPLE FUNC", funcname
            _compile_func_args_and_body(compiler, code, name, params, body)
    else:
        _compile_case_function(compiler, code, node, funcname, funcs)

    if api.isempty(funcname):
        return

    index = _declare_local(compiler, funcname)

    funcname_index = _declare_literal(compiler, funcname)
    code.emit_2(STORE_LOCAL, index, funcname_index, info(node))

# now they are identical except of scope
_compile_FUN = _compile_DEF


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
    if nodes.is_empty_node(elsebranch):
        _emit_nil(code)
    else:
        _compile(compiler, code, elsebranch[1])

    code.emit_1(LABEL, endif, codeinfo_unknown())


def _compile_TRY(compiler, code, node):
    trynode = node_first(node)
    catch = node_second(node)
    catchvar = catch[0]
    catchnode = catch[1]
    finallynode = node_third(node)
    finallylabel = code.prealocate_label()

    catchlabel = code.prealocate_label()
    code.emit_1(PUSH_CATCH, catchlabel, codeinfo_unknown())
    _compile(compiler, code, trynode)
    code.emit_0(POP_CATCH, codeinfo_unknown())
    code.emit_1(JUMP, finallylabel, codeinfo_unknown())

    # exception on top of the stack due to internal process/routine logic
    code.emit_1(LABEL, catchlabel, codeinfo_unknown())
    if not nodes.is_empty_node(catchvar):
        _emit_store_name(compiler, code, catchvar)
    else:
        _emit_pop(code)

    _compile(compiler, code, catchnode)

    code.emit_1(JUMP, finallylabel, codeinfo_unknown())
    code.emit_1(LABEL, finallylabel, codeinfo_unknown())
    if not nodes.is_empty_node(finallynode):
        _compile(compiler, code, finallynode)


############################
# IMPORT
#############################

def _dot_to_string(compiler, node):
    if node_type(node) == NT_LOOKUP_SYMBOL:
        return _dot_to_string(compiler, node_first(node)) + '.' + nodes.node_value(node_second(node))
    else:
        return nodes.node_value(node)


def _compile_LOAD(compiler, code, node):
    exp = node_first(node)
    if node_type(exp) == NT_AS:
        import_name = node_second(exp)
        module_path = _dot_to_string(compiler, node_first(exp))
    elif node_type(exp) == NT_LOOKUP_SYMBOL:
        import_name = node_second(exp)
        module_path = _dot_to_string(compiler, exp)
    else:
        assert node_type(exp) == NT_NAME
        import_name = exp
        module_path = nodes.node_value(exp)

    module_path_literal = _declare_literal(compiler, space.newsymbol_py_str(compiler.process, module_path))
    code.emit_1(LOAD, module_path_literal, info(node))

    _emit_store_name(compiler, code, import_name)


def _compile_MODULE(compiler, code, node):
    name_node = node_first(node)
    body = node_second(node)

    compiled_code = compile_ast(compiler, body)
    # _enter_scope(compiler)
    #
    # modulecode = newcode(compiler)
    #
    # _compile(compiler, modulecode, body)
    # current_scope = _current_scope(compiler)
    # scope = current_scope.finalize()
    # _exit_scope(compiler)
    # compiled_code = modulecode.finalize_compilation(scope)

    module_name = space.newsymbol_py_str(compiler.process, _get_name_value(name_node))
    module = space.newenvsource(module_name, compiled_code)
    module_index = _declare_literal(compiler, module)
    code.emit_1(MODULE, module_index, info(node))

    _emit_store(compiler, code, module_name, name_node)
    # module_name_index = _declare_local(compiler, module_name)
    # module_name_literal_index = _declare_literal(compiler, module_name)
    # code.emit_2(STORE_LOCAL, module_name_index, module_name_literal_index, info(name_node))


def _compile_GENERIC(compiler, code, node):
    name_node = node_first(node)
    name_value = _get_name_value(name_node)

    name = space.newsymbol_py_str(compiler.process, name_value)

    name_index = _declare_literal(compiler, name)
    index = _declare_local(compiler, name)
    code.emit_1(GENERIC, name_index, info(node))
    code.emit_2(STORE_LOCAL, index, name_index, info(name_node))

    if node_arity(node) == 2:
        methods = node_second(node)
        _emit_specify(compiler, code, node, methods)


def _compile_TRAIT(compiler, code, node):
    names = node_first(node)
    for name in names:
        name = space.newsymbol_py_str(compiler.process, nodes.node_value(name))
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
    _compile_node_name_lookup(compiler, code, name)
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
    name = space.newsymbol_py_str(compiler.process, nodes.node_value(vars[0]))
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


def _compile_CONS(compiler, code, node):
    _on_binary_primitive(compiler, code, node, internals.CONS)


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


####
# MAIN SWITCH
####


def _compile(compiler, code, ast):
    if nodes.is_list_node(ast):
        _compile_nodes(compiler, code, ast)
    else:
        _compile_node(compiler, code, ast)


def _compile_nodes(compiler, code, ast):
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
    elif NT_SPECIAL_NAME == ntype:
        _compile_SPECIAL_NAME(compiler, code, node)
    elif NT_SYMBOL == ntype:
        _compile_SYMBOL(compiler, code, node)

    elif NT_DEF == ntype:
        _compile_DEF(compiler, code, node)
    elif NT_FUN == ntype:
        _compile_FUN(compiler, code, node)

    elif NT_IF == ntype:
        _compile_IF(compiler, code, node)
    elif NT_WHEN == ntype:
        _compile_WHEN(compiler, code, node)
    elif NT_WHEN_NO_ELSE == ntype:
        _compile_WHEN_NO_ELSE(compiler, code, node)
    elif NT_MATCH == ntype:
        _compile_MATCH(compiler, code, node)
    elif NT_TRY == ntype:
        _compile_TRY(compiler, code, node)

    elif NT_LOAD == ntype:
        _compile_LOAD(compiler, code, node)
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

    elif NT_LOOKUP == ntype:
        _compile_LOOKUP(compiler, code, node)
    elif NT_LOOKUP_SYMBOL == ntype:
        _compile_LOOKUP_SYMBOL(compiler, code, node)

    elif NT_MODIFY == ntype:
        _compile_MODIFY(compiler, code, node)
    elif NT_CONS == ntype:
        _compile_CONS(compiler, code, node)

    elif NT_IN == ntype:
        _compile_IN(compiler, code, node)
    elif NT_NOTIN == ntype:
        _compile_NOTIN(compiler, code, node)
    elif NT_IS == ntype:
        _compile_IS(compiler, code, node)
    elif NT_ISNOT == ntype:
        _compile_ISNOT(compiler, code, node)
    elif NT_ISA == ntype:
        _compile_ISA(compiler, code, node)
    elif NT_NOTA == ntype:
        _compile_NOTA(compiler, code, node)
    elif NT_KINDOF == ntype:
        _compile_KINDOF(compiler, code, node)

    elif NT_AND == ntype:
        _compile_AND(compiler, code, node)
    elif NT_OR == ntype:
        _compile_OR(compiler, code, node)
    elif NT_NOT == ntype:
        _compile_NOT(compiler, code, node)
    elif NT_EQ == ntype:
        _compile_EQ(compiler, code, node)
    elif NT_LE == ntype:
        _compile_LE(compiler, code, node)
    elif NT_GE == ntype:
        _compile_GE(compiler, code, node)
    elif NT_NE == ntype:
        _compile_NE(compiler, code, node)
    elif NT_BITAND == ntype:
        _compile_BITAND(compiler, code, node)
    elif NT_BITNOT == ntype:
        _compile_BITNOT(compiler, code, node)
    elif NT_BITOR == ntype:
        _compile_BITOR(compiler, code, node)
    elif NT_BITXOR == ntype:
        _compile_BITXOR(compiler, code, node)
    elif NT_SUB == ntype:
        _compile_SUB(compiler, code, node)
    elif NT_ADD == ntype:
        _compile_ADD(compiler, code, node)
    elif NT_MUL == ntype:
        _compile_MUL(compiler, code, node)
    elif NT_DIV == ntype:
        _compile_DIV(compiler, code, node)
    elif NT_MOD == ntype:
        _compile_MOD(compiler, code, node)
    elif NT_LT == ntype:
        _compile_LT(compiler, code, node)
    elif NT_GT == ntype:
        _compile_GT(compiler, code, node)

    elif NT_RSHIFT == ntype:
        _compile_RSHIFT(compiler, code, node)
    elif NT_URSHIFT == ntype:
        _compile_URSHIFT(compiler, code, node)
    elif NT_LSHIFT == ntype:
        _compile_LSHIFT(compiler, code, node)

    elif NT_UNARY_PLUS == ntype:
        _compile_UNARY_PLUS(compiler, code, node)
    elif NT_UNARY_MINUS == ntype:
        _compile_UNARY_MINUS(compiler, code, node)

    elif NT_GOTO == ntype:
        _compile_GOTO(compiler, code, node)

    elif NT_ASSIGN == ntype:
        _compile_ASSIGN(compiler, code, node)
    else:
        compile_error(compiler, code, node, u"Unknown node")


def newcode(compiler):
    return CodeSource(SourceInfo(compiler.source_path, compiler.source))


def compile_ast(compiler, ast):
    code = newcode(compiler)
    _enter_scope(compiler)
    _declare_arguments(compiler, 0, False)
    _compile(compiler, code, ast)
    scope = _current_scope(compiler)
    final_scope = scope.finalize()
    _exit_scope(compiler)
    compiled_code = code.finalize_compilation(final_scope)
    return compiled_code


def compile(process, src, sourcename):
    ast = parser.parse_string(src)
    # print ast
    compiler = Compiler(process, sourcename, src)
    code = compile_ast(compiler, ast)
    return code


def compile_env(process, modulename, src, sourcename):
    code = compile(process, src, sourcename)
    module = space.newenvsource(modulename, code)
    return module


def compile_function_source(process, src, name):
    code = compile(process, src, name)
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
