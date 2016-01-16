__author__ = 'gloryofrobots'
from obin.compile.parse.node import (is_empty_node, is_list_node, is_iterable_node,
                                     create_tuple_node, is_wildcard_node)
from obin.compile.parse.parser import *
from obin.compile.scope import Scope
from obin.types import space as obs
from obin.types import api
from obin.builtins.internals import internals
from obin.compile.code.source import CodeSource, codeinfo, codeinfo_unknown, SourceInfo
from obin.compile.code import *
from obin.utils.misc import is_absent_index


def compile_error(process, node, message):
    error_message = "Compile Error %d:%d %s" % (node.line, node.position, message)
    raise RuntimeError(error_message)


def compile_error_1(process, node, message, arg):
    error_message = "Compile Error %d:%d %s" % (node.line, node.position, message)
    raise RuntimeError(error_message, arg)


def string_unquote(string):
    s = string
    if s.startswith('"'):
        assert s.endswith('"')
    else:
        assert s.startswith("'")
        assert s.endswith("'")
    s = s[:-1]
    s = s[1:]

    return s


class Compiler:
    def __init__(self, path, src):
        self.scopes = []
        self.depth = -1
        self.source_path = path
        self.source = src


def info(node):
    if is_empty_node(node):
        return codeinfo_unknown()
    return codeinfo(node.position, node.line, node.column)


########################
# SCOPES
########################


def _enter_scope(process, compiler):
    compiler.depth += 1

    new_scope = Scope()
    compiler.scopes.append(new_scope)
    # print 'starting new scope %d' % (process, compiler.depth, )


def _is_modifiable_binding(process, compiler, name):
    scope = _current_scope(process, compiler)
    if not is_absent_index(scope.get_local_index(name)):
        return True
    if scope.has_outer(name):
        return True

    return False


def _declare_outer(process, compiler, symbol):
    assert obs.issymbol(symbol)
    scope = _current_scope(process, compiler)
    if not scope.is_function_scope():
        compile_error_1(process, compiler.current_node,
                        "Outer variables can be declared only inside functions", symbol)
    if scope.has_outer(symbol):
        compile_error_1(process, compiler.current_node, "Outer variable has already been declared", symbol)
    scope.add_outer(symbol)


def _declare_arguments(process, compiler, args, varargs):
    _current_scope(process, compiler).add_arguments(args, varargs)


def _declare_function_name(process, compiler, name):
    _current_scope(process, compiler).add_function_name(name)


def _declare_reference(process, compiler, symbol):
    assert obs.issymbol(symbol)
    scope = _current_scope(process, compiler)
    idx = scope.get_reference(symbol)
    if is_absent_index(idx):
        idx = scope.add_reference(symbol)
    return idx


def _declare_literal(process, compiler, literal):
    assert obs.isany(literal)
    scope = _current_scope(process, compiler)
    idx = scope.get_literal(literal)
    if is_absent_index(idx):
        idx = scope.add_literal(literal)
    return idx


def _declare_local(process, compiler, symbol):
    assert obs.issymbol(symbol)
    assert not api.isempty(symbol)
    scope = _current_scope(process, compiler)
    idx = scope.get_local_index(symbol)
    if not is_absent_index(idx):
        return idx

    idx = scope.add_local(symbol)
    assert not is_absent_index(idx)
    return idx


def _get_variable_index(process, compiler, name):
    """
        return var_index, is_local_variable
    """
    scope_id = 0
    for scope in reversed(compiler.scopes):
        idx = scope.get_local_index(name)
        if not is_absent_index(idx):
            if scope_id == 0:
                return idx, True
            else:
                # TODO here can be optimisation where we can calculate number of scopes to find back variable
                ref_id = _declare_reference(process, compiler, name)
                return ref_id, False
        scope_id += 1

    # compile_error(process,process, compiler.current_node, "Non reachable variable", name)
    # COMMENT ERROR BECAUSE OF LATER LINKING OF BUILTINS
    ref_id = _declare_reference(process, compiler, name)
    return ref_id, False


def _declare_variable(process, compiler, symbol):
    """
        return var_index, is_local
    """

    scope = _current_scope(process, compiler)
    if scope.has_outer(symbol):
        idx = _declare_reference(process, compiler, symbol)
        return idx, False

    idx = _declare_local(process, compiler, symbol)
    return idx, True


def _exit_scope(process, compiler):
    compiler.depth = compiler.depth - 1
    compiler.scopes.pop()
    # print 'closing scope, returning to %d' % (process, compiler.depth, )


def _current_scope(process, compiler):
    return compiler.scopes[-1]


"""
    HOOKS
"""


def _compile_FLOAT(process, compiler, code, node):
    value = float(node.value)
    idx = _declare_literal(process, compiler, obs.newfloat(value))
    code.emit_1(LITERAL, idx, info(node))


def _compile_INT(process, compiler, code, node):
    value = int(node.value)
    idx = _declare_literal(process, compiler, obs.newint(value))
    code.emit_1(LITERAL, idx, info(node))


def _emit_integer(process, compiler, code, integer):
    idx = _declare_literal(process, compiler, obs.newint(integer))
    code.emit_1(LITERAL, idx, codeinfo_unknown())


def _compile_TRUE(process, compiler, code, node):
    code.emit_0(TRUE, info(node))


def _compile_FALSE(process, compiler, code, node):
    code.emit_0(FALSE, info(node))


def _compile_NIL(process, compiler, code, node):
    code.emit_0(NULL, info(node))


def _compile_UNDEFINED(process, compiler, code, node):
    code.emit_0(UNDEFINED, info(node))


def _get_name_value(name):
    if name.node_type == NT_SPECIAL_NAME:
        value = _get_special_name_value(name)
    elif name.node_type == NT_NAME:
        value = name.value
    else:
        assert False, "Invalid call"
    return value


def _emit_pop(code):
    code.emit_0(POP, codeinfo_unknown())


def _emit_dup(code):
    code.emit_0(DUP, codeinfo_unknown())


def _emit_undefined(code):
    code.emit_0(UNDEFINED, codeinfo_unknown())


def _emit_symbol_name(process, compiler, code, name):
    value = _get_name_value(name)
    symbol = obs.newsymbol_py_str(process, value)
    idx = _declare_literal(process, compiler, symbol)
    code.emit_1(LITERAL, idx, info(name))


def _compile_STR(process, compiler, code, node):
    from obin.runistr import unicode_unescape, decode_str_utf8

    strval = str(node.value)
    strval = decode_str_utf8(strval)
    strval = string_unquote(strval)
    strval = unicode_unescape(strval)
    string = obs.newstring(strval)
    idx = _declare_literal(process, compiler, string)
    code.emit_1(LITERAL, idx, info(node))


def _compile_CHAR(process, compiler, code, node):
    from obin.runistr import unicode_unescape, decode_str_utf8
    # TODO CHAR

    strval = str(node.value)
    strval = decode_str_utf8(strval)
    strval = string_unquote(strval)
    strval = unicode_unescape(strval)
    string = obs.newstring(strval)
    idx = _declare_literal(process, compiler, string)
    code.emit_1(LITERAL, idx, info(node))


# def _compile_OUTER(process, compiler, code, node):
#     # TODO REMOVE IT
#     assert False, "Why you need it?"
#     name = obs.newstring_from_str(node.first().value)
#     _declare_outer(process, compiler, name)


def _on_binary_primitive(process, compiler, code, node, name):
    _compile(process, compiler, code, node.first())
    _compile(process, compiler, code, node.second())
    code.emit_1(CALL_INTERNAL, name, info(node))


def _on_unary_primitive(process, compiler, code, node, name):
    _compile(process, compiler, code, node.first())
    code.emit_1(CALL_INTERNAL, name, info(node))


def _compile_BITAND(process, compiler, code, node):
    _on_binary_primitive(process, compiler, code, node, internals.BITAND)


def _compile_BITOR(process, compiler, code, node):
    _on_binary_primitive(process, compiler, code, node, internals.BITOR)


def _compile_BITXOR(process, compiler, code, node):
    _on_binary_primitive(process, compiler, code, node, internals.BITXOR)


def _compile_UNARY_PLUS(process, compiler, code, node):
    _on_unary_primitive(process, compiler, code, node, internals.UPLUS)


def _compile_ADD(process, compiler, code, node):
    _on_binary_primitive(process, compiler, code, node, internals.ADD)


def _compile_MUL(process, compiler, code, node):
    _on_binary_primitive(process, compiler, code, node, internals.MUL)


def _compile_MOD(process, compiler, code, node):
    _on_binary_primitive(process, compiler, code, node, internals.MOD)


def _compile_DIV(process, compiler, code, node):
    _on_binary_primitive(process, compiler, code, node, internals.DIV)


def _compile_UNARY_MINUS(process, compiler, code, node):
    _on_unary_primitive(process, compiler, code, node, internals.UMINUS)


def _compile_SUB(process, compiler, code, node):
    _on_binary_primitive(process, compiler, code, node, internals.SUB)


def _compile_BITNOT(process, compiler, code, node):
    _on_unary_primitive(process, compiler, code, node, internals.BITNOT)


def _compile_NOT(process, compiler, code, node):
    _on_unary_primitive(process, compiler, code, node, internals.NOT)


def _compile_GE(process, compiler, code, node):
    _on_binary_primitive(process, compiler, code, node, internals.GE)


def _compile_GT(process, compiler, code, node):
    _on_binary_primitive(process, compiler, code, node, internals.GT)


def _compile_LE(process, compiler, code, node):
    _on_binary_primitive(process, compiler, code, node, internals.LE)


def _compile_LT(process, compiler, code, node):
    _on_binary_primitive(process, compiler, code, node, internals.LT)


def _compile_IS(process, compiler, code, node):
    _on_binary_primitive(process, compiler, code, node, internals.IS)


def _compile_ISNOT(process, compiler, code, node):
    _on_binary_primitive(process, compiler, code, node, internals.ISNOT)


def _compile_IN(process, compiler, code, node):
    _on_binary_primitive(process, compiler, code, node, internals.IN)


def _compile_EQ(process, compiler, code, node):
    _on_binary_primitive(process, compiler, code, node, internals.EQ)


def _compile_NE(process, compiler, code, node):
    _on_binary_primitive(process, compiler, code, node, internals.NE)


def _compile_LSHIFT(process, compiler, code, node):
    _on_binary_primitive(process, compiler, code, node, internals.LSH)


def _compile_RSHIFT(process, compiler, code, node):
    _on_binary_primitive(process, compiler, code, node, internals.RSH)


def _compile_URSHIFT(process, compiler, code, node):
    _on_binary_primitive(process, compiler, code, node, internals.URSH)


def _compile_AND(process, compiler, code, node):
    _compile(process, compiler, code, node.first())
    one = code.prealocate_label()
    code.emit_1(JUMP_IF_FALSE_NOPOP, one, info(node))
    _compile(process, compiler, code, node.second())
    code.emit_1(LABEL, one, info(node))


def _compile_OR(process, compiler, code, node):
    _compile(process, compiler, code, node.first())
    one = code.prealocate_label()
    code.emit_1(JUMP_IF_TRUE_NOPOP, one, info(node))
    _compile(process, compiler, code, node.second())
    code.emit_1(LABEL, one, info(node))


def _compile_ASSIGN_MEMBER(process, compiler, code, node):
    member = node.first()
    value = node.second()
    obj = member.first()
    item = member.second()

    _compile(process, compiler, code, value)
    _compile(process, compiler, code, item)
    _compile(process, compiler, code, obj)
    code.emit_0(STORE_MEMBER, info(node))


def _compile_ASSIGN_SYMBOL(process, compiler, code, node):
    member = node.first()

    obj = member.first()
    _compile(process, compiler, code, node.second())
    _emit_symbol_name(process, compiler, code, member.second())
    _compile(process, compiler, code, obj)
    code.emit_0(STORE_MEMBER, info(node))


def _emit_store_name(process, compiler, code, namenode):
    name = obs.newsymbol_py_str(process, namenode.value)
    index, is_local = _declare_variable(process, compiler, name)

    name_index = _declare_literal(process, compiler, name)
    if is_local:
        code.emit_2(STORE_LOCAL, index, name_index, info(namenode))
    else:
        code.emit_2(STORE_OUTER, index, name_index, info(namenode))


#########################################################

PATTERN_DATA = """
    match [1, 2, 3]:
        case {age=41, name="Bob"}: (name, age) end
        case {name="Bob", surname=("Alice", "Dou")}: (surname, name) end
    end
"""


def _compile_MATCH(process, compiler, code, node):
    from obin.compile.match import transform
    from obin.compile.parse.node import create_goto_node
    from obin.compile import MATCH_SYS_VAR
    exp = node.first()
    patterns = node.second()

    name = obs.newsymbol_py_str(process, MATCH_SYS_VAR)

    name_index = _declare_literal(process, compiler, name)
    index = _declare_local(process, compiler, name)
    _compile(process, compiler, code, exp)
    code.emit_2(STORE_LOCAL, index, name_index, codeinfo_unknown())

    endmatch = code.prealocate_label()
    graph = transform(process, compiler, node, patterns, create_goto_node(endmatch))
    _compile(process, compiler, code, graph)
    code.emit_1(LABEL, endmatch, codeinfo_unknown())


def _compile_GOTO(process, compiler, code, node):
    # TODO REMOVE THIS SHIT
    # WE NEED TO REMOVE POPS ON GOTO BECAUSE OF AUTOMATIC POP INSERTION
    # GOTO USED ONLY FOR JUMPS ON PATTERN MATCHING BECAUSE IN PM WE PRODUCE TREE OF IFS
    # AND NEED JUMP FROM SUCCESS BRANCH. IT'S ACTUALLY SIMPLIFIES COMPILATION BUT LEEDS TO THIS BAD DESIGN
    # SOLUTION: REMOVE AUTO POPS, SOMEHOW

    last_code = code.last()
    if last_code[0] == POP:
        code.remove_last()

    value = int(node.value)
    code.emit_1(JUMP, value, codeinfo_unknown())


#########################################################
#####
# DESTRUCT DESTRUCT
####
def _compile_destruct(process, compiler, code, node):
    _compile(process, compiler, code, node.second())
    return _compile_destruct_recur(process, compiler, code, node.first())


def _is_optimizable_unpack_seq_pattern(node):
    items = node.first()
    for child in items:
        if child is None:
            print ""
        if child.node_type != NT_NAME:
            return False
    return True


def _compile_destruct_recur(process, compiler, code, node):
    if node.node_type == NT_TUPLE:
        # x,y,z = foo() optimisation to single unpack opcode
        if _is_optimizable_unpack_seq_pattern(node):
            return _compile_destruct_unpack_seq(process, compiler, code, node)
        else:
            return _compile_destruct_recur_seq(process, compiler, code, node)
    elif node.node_type == NT_MAP:
        return _compile_destruct_recur_map(process, compiler, code, node)
    else:
        compile_error(process, node, "unsupported assignment syntax")


def _compile_destruct_recur_map(process, compiler, code, node):
    pairs = node.first()
    for pair in pairs:
        _emit_dup(code)

        key = pair[0]
        value = pair[1]
        varname = None
        if is_empty_node(value):
            varname = key
        elif value.node_type == NT_NAME:
            varname = value

        _emit_map_key(process, compiler, code, key)

        code.emit_0(MEMBER, info(key))

        if varname is None:
            _compile_destruct_recur(process, compiler, code, value)
            _emit_pop(code)
        else:
            _emit_store_name(process, compiler, code, varname)
            _emit_pop(code)


##################################################
# DESTRUCT SEQUENCE
##################################################

def _compile_destruct_recur_seq_rest(process, compiler, code, last_item, last_index):
    _emit_dup(code)
    varname = last_item.first()
    _emit_integer(process, compiler, code, last_index)
    code.emit_0(UNDEFINED, codeinfo_unknown())
    code.emit_0(SLICE, codeinfo_unknown())
    _emit_store_name(process, compiler, code, varname)
    _emit_pop(code)


def _compile_destruct_recur_seq_item(process, compiler, code, item, index):
    _emit_dup(code)

    varname = None
    if item.node_type == NT_NAME:
        varname = item

    idx = _declare_literal(process, compiler, obs.newint(index))
    code.emit_1(LITERAL, idx, info(item))
    code.emit_0(MEMBER, info(item))

    if varname is None:
        _compile_destruct_recur(process, compiler, code, item)
        _emit_pop(code)
    else:
        _emit_store_name(process, compiler, code, varname)
        _emit_pop(code)


def _compile_destruct_recur_seq(process, compiler, code, node):
    items = node.first()
    length = len(items)

    last_index = length - 1

    for i in range(last_index):
        item = items[i]
        _compile_destruct_recur_seq_item(process, compiler, code, item, i)

    last_item = items[last_index]
    if last_item.node_type == NT_REST:
        _compile_destruct_recur_seq_rest(process, compiler, code, last_item, last_index)
    else:
        _compile_destruct_recur_seq_item(process, compiler, code, last_item, last_index)


def _compile_destruct_unpack_seq(process, compiler, code, node):
    _emit_dup(code)
    names = node.first()
    length = len(names)
    code.emit_1(UNPACK_SEQUENCE, length, info(node))
    for name in names[0:-1]:
        _emit_store_name(process, compiler, code, name)
        _emit_pop(code)
    last_name = names[-1]
    _emit_store_name(process, compiler, code, last_name)
    _emit_pop(code)


################################################################################

def _compile_ASSIGN(process, compiler, code, node):
    left = node.first()
    if left.node_type == NT_LOOKUP_SYMBOL:
        return _compile_ASSIGN_SYMBOL(process, compiler, code, node)
    elif left.node_type == NT_LOOKUP:
        return _compile_ASSIGN_MEMBER(process, compiler, code, node)
    elif left.node_type == NT_TUPLE or left.node_type == NT_MAP:
        return _compile_destruct(process, compiler, code, node)

    _compile(process, compiler, code, node.second())
    _emit_store_name(process, compiler, code, left)


def _compile_modify_assignment_dot_primitive(process, compiler, code, node, operation):
    member = node.first()

    obj = member.first()

    _compile(process, compiler, code, node.first())
    _compile(process, compiler, code, node.second())
    code.emit_1(CALL_INTERNAL, operation, info(obj))

    _emit_symbol_name(process, compiler, code, member.second())
    _compile(process, compiler, code, obj)
    code.emit_0(STORE_MEMBER, info(obj))


def _compile_modify_assignment_primitive(process, compiler, code, node, operation):
    left = node.first()
    if left.node_type == NT_LOOKUP_SYMBOL:
        return _compile_modify_assignment_dot_primitive(process, compiler, code, node, operation)

    name = obs.newsymbol_py_str(process, left.value)
    if not _is_modifiable_binding(process, compiler, name):
        compile_error_1(process, node, "Unreachable variable", name)

    # _compile(process, compiler,code, left)
    _compile(process, compiler, code, node.first())
    _compile(process, compiler, code, node.second())
    code.emit_1(CALL_INTERNAL, operation, info(node))
    _emit_store_name(process, compiler, code, left)


def _compile_ADD_ASSIGN(process, compiler, code, node):
    _compile_modify_assignment_primitive(process, compiler, code, node, internals.ADD)


def _compile_SUB_ASSIGN(process, compiler, code, node):
    _compile_modify_assignment_primitive(process, compiler, code, node, internals.SUB)


def _compile_MUL_ASSIGN(process, compiler, code, node):
    _compile_modify_assignment_primitive(process, compiler, code, node, internals.MUL)


def _compile_DIV_ASSIGN(process, compiler, code, node):
    _compile_modify_assignment_primitive(process, compiler, code, node, internals.DIV)


def _compile_MOD_ASSIGN(process, compiler, code, node):
    _compile_modify_assignment_primitive(process, compiler, code, node, internals.MOD)


def _compile_BITOR_ASSIGN(process, compiler, code, node):
    _compile_modify_assignment_primitive(process, compiler, code, node, internals.BITOR)


def _compile_BITAND_ASSIGN(process, compiler, code, node):
    _compile_modify_assignment_primitive(process, compiler, code, node, internals.BITAND)


def _compile_BITXOR_ASSIGN(process, compiler, code, node):
    _compile_modify_assignment_primitive(process, compiler, code, node, internals.BITXOR)


def _compile_node_name_lookup(process, compiler, code, node):
    name_value = _get_name_value(node)
    name = obs.newsymbol_py_str(process, name_value)

    index, is_local = _get_variable_index(process, compiler, name)
    name_index = _declare_literal(process, compiler, name)
    if is_local:
        code.emit_2(LOCAL, index, name_index, info(node))
    else:
        code.emit_2(OUTER, index, name_index, info(node))


def _get_special_name_value(node):
    # REMOVE BACKTICKS `xxx`
    return node.value[1:len(node.value) - 1]


def _compile_SPECIAL_NAME(process, compiler, code, node):
    _compile_node_name_lookup(process, compiler, code, node)


def _compile_NAME(process, compiler, code, node):
    _compile_node_name_lookup(process, compiler, code, node)


def _compile_SYMBOL(process, compiler, code, node):
    name = node.first()
    _emit_symbol_name(process, compiler, code, name)


def _compile_RETURN(process, compiler, code, node):
    expr = node.first()
    if is_empty_node(expr):
        _emit_undefined(code)
    else:
        _compile(process, compiler, code, expr)

    code.emit_0(RETURN, info(node))


def _compile_THROW(process, compiler, code, node):
    expr = node.first()
    if is_empty_node(expr):
        _emit_undefined(code)
    else:
        _compile(process, compiler, code, expr)

    code.emit_0(THROW, info(node))


def _emit_map_key(process, compiler, code, key):
    if key.node_type == NT_NAME:
        # in case of names in object literal we must convert them to symbols
        _emit_symbol_name(process, compiler, code, key)
    else:
        _compile(process, compiler, code, key)


def _compile_MAP(process, compiler, code, node):
    items = node.first()
    for c in items:
        key = c[0]
        value = c[1]
        if is_empty_node(value):
            _compile_NIL(process, compiler, code, value)
        else:
            _compile(process, compiler, code, value)

        _emit_map_key(process, compiler, code, key)

    code.emit_1(MAP, len(items), info(node))


def _compile_TUPLE(process, compiler, code, node):
    items = node.first()
    for c in items:
        _compile(process, compiler, code, c)

    code.emit_1(TUPLE, len(items), info(node))


def _compile_LIST(process, compiler, code, node):
    items = node.first()
    for c in items:
        _compile(process, compiler, code, c)

    code.emit_1(LIST, len(items), info(node))


# def _emit_list(process, compiler, code, node):
#     items = node.first()
#
#     for c in items:
#         _compile(process, compiler, code, c)
#
#     code.emit_1(LIST, len(items))


def _compile_BREAK(process, compiler, code, node):
    _emit_undefined(code)
    if not code.emit_break():
        compile_error(process, node, "break outside loop")


def _compile_CONTINUE(process, compiler, code, node):
    _emit_undefined(code)
    if not code.emit_continue():
        compile_error(process, node, "continue outside loop")


def _compile_func_args_and_body(process, compiler, code, funcname, params, outers, body, opcode, emitinfo):
    _enter_scope(process, compiler)

    funccode = newcode(compiler)

    if is_empty_node(params):
        _declare_arguments(process, compiler, None, None)
    else:
        args = params.first()
        length = args.length()
        funccode.emit_0(ARGUMENTS, codeinfo_unknown())

        # TODO REMOVE
        _declare_arguments(process, compiler, [obs.newstring(u"$%d" % i) for i in range(length)], None)
        _compile_destruct_recur(process, compiler, funccode, params)

    if is_iterable_node(outers):
        for outer in outers:
            _declare_outer(process, compiler, obs.newsymbol_py_str(process, outer.value))

    # avoid recursive name lookups for origins because in this case
    # index will be pointed to constructor function instead of origin
    if not api.isempty(funcname) and not opcode == ORIGIN:
        _declare_function_name(process, compiler, funcname)

    _compile(process, compiler, funccode, body)
    current_scope = _current_scope(process, compiler)
    scope = current_scope.finalize()
    _exit_scope(process, compiler)
    # print "LOCALS:", str(scope.variables.keys())
    # print "REFS:", str(scope.references)
    compiled_code = funccode.finalize_compilation(scope)
    # print [str(c) for c in compiled_code.opcodes]
    # print "-------------------------"

    source = obs.newfuncsource(funcname, compiled_code)
    source_index = _declare_literal(process, compiler, source)
    code.emit_1(opcode, source_index, emitinfo)


def _compile_FUNC(process, compiler, code, node):
    name = node.first()
    if not is_empty_node(name):
        funcname = obs.newsymbol_py_str(process, name.value)
    else:
        funcname = obs.newsymbol_py_str(process, "")

    params = node.second()
    outers = node.third()
    body = node.fourth()
    _compile_func_args_and_body(process, compiler, code, funcname, params, outers, body, FUNCTION, info(name))

    if api.isempty(funcname):
        return

    index = _declare_local(process, compiler, funcname)

    funcname_index = _declare_literal(process, compiler, funcname)
    code.emit_2(STORE_LOCAL, index, funcname_index, info(node))


def _compile_ORIGIN(process, compiler, code, node):
    name = node.first()
    funcname = obs.newsymbol_py_str(process, name.value)
    funcname_index = _declare_literal(process, compiler, funcname)
    index = _declare_local(process, compiler, funcname)

    params = node.second()
    outers = node.third()
    body = node.fourth()
    _compile_func_args_and_body(process, compiler, code, funcname, params, outers, body, ORIGIN, info(node))

    code.emit_2(STORE_LOCAL, index, funcname_index, info(name))


def _compile_branch(process, compiler, code, condition, body, endif):
    _compile(process, compiler, code, condition)
    end_body = code.prealocate_label()
    code.emit_1(JUMP_IF_FALSE, end_body, info(condition))
    _compile(process, compiler, code, body)
    code.emit_1(JUMP, endif, codeinfo_unknown())
    code.emit_1(LABEL, end_body, codeinfo_unknown())


def _compile_WHEN(process, compiler, code, node):
    condition = node.first()
    truebranch = node.second()
    falsebranch = node.third()
    endif = code.prealocate_label()
    _compile_branch(process, compiler, code, condition, truebranch, endif)
    _compile(process, compiler, code, falsebranch)
    code.emit_1(LABEL, endif, codeinfo_unknown())


def _compile_IF(process, compiler, code, node):
    branches = node.first()

    endif = code.prealocate_label()

    for i in range(len(branches) - 1):
        branch = branches[i]
        _compile_branch(process, compiler, code, branch[0], branch[1], endif)

    elsebranch = branches[-1]
    if is_empty_node(elsebranch):
        _emit_undefined(code)
    else:
        _compile(process, compiler, code, elsebranch[1])

    code.emit_1(LABEL, endif, codeinfo_unknown())


def _compile_TRY(process, compiler, code, node):
    trynode = node.first()
    catch = node.second()
    catchvar = catch[0]
    catchnode = catch[1]
    finallynode = node.third()
    if not is_empty_node(finallynode):
        finallylabel = code.prealocate_label()
    else:
        finallylabel = None

    catchlabel = code.prealocate_label()
    code.emit_1(PUSH_CATCH, catchlabel, codeinfo_unknown())
    _compile(process, compiler, code, trynode)
    code.emit_0(POP_CATCH, codeinfo_unknown())
    if finallylabel is not None:
        code.emit_1(JUMP, finallylabel, codeinfo_unknown())

    code.emit_1(LABEL, catchlabel, codeinfo_unknown())
    _emit_store_name(process, compiler, code, catchvar)
    _compile(process, compiler, code, catchnode)

    if finallylabel is not None:
        code.emit_1(JUMP, finallylabel, codeinfo_unknown())
        code.emit_1(LABEL, finallylabel, codeinfo_unknown())
        _compile(process, compiler, code, finallynode)


############################
# IMPORT
#############################

def _dot_to_string(process, compiler, node):
    if node.node_type == NT_LOOKUP_SYMBOL:
        return _dot_to_string(process, compiler, node.first()) + '.' + node.second().value
    else:
        return node.value


def _compile_IMPORT_STMT(process, compiler, code, node):
    exp = node.first()
    if exp.node_type == NT_AS:
        import_name = exp.second()
        module_path = _dot_to_string(process, compiler, exp.first())
    elif exp.node_type == NT_LOOKUP_SYMBOL:
        import_name = exp.second()
        module_path = _dot_to_string(process, compiler, exp)
    else:
        assert exp.node_type == NT_NAME
        import_name = exp
        module_path = exp.value

    module_path_literal = _declare_literal(process, compiler, obs.newstring_from_str(module_path))
    code.emit_1(IMPORT, module_path_literal, info(node))

    _emit_store_name(process, compiler, code, import_name)


def _compile_IMPORT_EXP(process, compiler, code, node):
    exp = node.first()
    if exp.node_type == NT_LOOKUP_SYMBOL:
        module_path = _dot_to_string(process, compiler, exp)
    else:
        assert exp.node_type == NT_NAME
        module_path = exp.value

    module_path = obs.newstring_from_str(module_path)
    module_path_literal = _declare_literal(process, compiler, module_path)
    code.emit_1(IMPORT, module_path_literal, info(node))


def _compile_IMPORT(process, compiler, code, node):
    if node.arity == 2:
        _compile_IMPORT_STMT(process, compiler, code, node)
    else:
        _compile_IMPORT_EXP(process, compiler, code, node)


def _compile_GENERIC(process, compiler, code, node):
    name_node = node.first()
    name_value = _get_name_value(name_node)

    name = obs.newsymbol_py_str(process, name_value)

    name_index = _declare_literal(process, compiler, name)
    index = _declare_local(process, compiler, name)
    code.emit_1(GENERIC, name_index, info(node))
    code.emit_2(STORE_LOCAL, index, name_index, info(name_node))

    if node.arity == 2:
        methods = node.second()
        _emit_specify(process, compiler, code, node, methods)


def _compile_TRAIT(process, compiler, code, node):
    name = node.first()
    name = obs.newsymbol_py_str(process, name.value)
    index = _declare_local(process, compiler, name)

    name_index = _declare_literal(process, compiler, name)
    code.emit_1(TRAIT, name_index, info(node))
    code.emit_2(STORE_LOCAL, index, name_index, info(node))


def _emit_specify(process, compiler, code, node, methods):
    for method in methods:
        method_args = method[0]
        method_body = method[1]
        args = []
        signature = []
        for arg in method_args:
            if arg.node_type == NT_OF:
                args.append(arg.first())
                signature.append(arg.second())
            else:
                args.append(arg)
                signature.append(None)

        for trait in signature:
            if trait is None:
                _emit_undefined(code)
            else:
                _compile(process, compiler, code, trait)

        code.emit_1(TUPLE, len(signature), info(node))

        method_name = obs.newsymbol(process, u"")
        args_node = create_tuple_node(node, args)
        _compile_func_args_and_body(process, compiler, code, method_name, args_node, empty_node(),
                                    method_body,
                                    FUNCTION, info(node))
        code.emit_1(TUPLE, 2, info(node))

    code.emit_1(SPECIFY, len(methods), info(node))


def _compile_SPECIFY(process, compiler, code, node):
    name = node.first()
    _compile_node_name_lookup(process, compiler, code, name)
    methods = node.second()
    _emit_specify(process, compiler, code, node, methods)


def _compile_FOR(process, compiler, code, node):
    source = node.second()
    body = node.third()
    _compile(process, compiler, code, source)
    code.emit_0(ITERATOR, info(node))
    # load the "last" iterations result
    _emit_undefined(code)
    precond = code.emit_startloop_label()
    code.continue_at_label(precond)
    finish = code.prealocate_endloop_label(False)
    # update = code.prealocate_updateloop_label()

    code.emit_1(JUMP_IF_ITERATOR_EMPTY, finish, codeinfo_unknown())

    # put next iterator value on stack
    code.emit_0(NEXT, codeinfo_unknown())

    vars = node.first()
    name = obs.newsymbol_py_str(process, vars[0].value)
    index = _declare_local(process, compiler, name)

    name_index = _declare_literal(process, compiler, name)
    code.emit_2(STORE_LOCAL, index, name_index, info(node))
    _emit_pop(code)

    _compile(process, compiler, code, body)
    # code.emit_updateloop_label(update)

    code.emit_1(JUMP, precond, codeinfo_unknown())
    code.emit_endloop_label(finish)


def _compile_WHILE(process, compiler, code, node):
    condition = node.first()
    body = node.second()
    _emit_undefined(code)
    startlabel = code.emit_startloop_label()
    code.continue_at_label(startlabel)
    _compile(process, compiler, code, condition)
    endlabel = code.prealocate_endloop_label()
    code.emit_1(JUMP_IF_FALSE, endlabel, codeinfo_unknown())
    _emit_pop(code)
    _compile(process, compiler, code, body)
    code.emit_1(JUMP, startlabel, codeinfo_unknown())
    code.emit_endloop_label(endlabel)
    code.done_continue()


def _compile_CONS(process, compiler, code, node):
    _on_binary_primitive(process, compiler, code, node, internals.CONS)


def _compile_LOOKUP_SYMBOL(process, compiler, code, node):
    obj = node.first()
    _compile(process, compiler, code, obj)
    _emit_symbol_name(process, compiler, code, node.second())
    code.emit_0(MEMBER, info(node))


def _emit_SLICE(process, compiler, code, obj, slice):
    start = slice.first()
    end = slice.second()

    _compile(process, compiler, code, obj)

    if is_wildcard_node(start):
        _emit_undefined(code)
    else:
        _compile(process, compiler, code, start)

    if is_wildcard_node(end):
        _emit_undefined(code)
    else:
        _compile(process, compiler, code, end)

    code.emit_0(SLICE, info(slice))


def _compile_LOOKUP(process, compiler, code, node):
    # TODO OPTIMISATION FOR INDEX LOOKUP
    obj = node.first()
    expr = node.second()
    if expr.node_type == NT_RANGE:
        return _emit_SLICE(process, compiler, code, obj, expr)

    _compile(process, compiler, code, obj)
    _compile(process, compiler, code, expr)
    code.emit_0(MEMBER, info(node))


def _compile_args_list(process, compiler, code, args):
    args_count = 0

    for arg in args:
        _compile(process, compiler, code, arg)
        args_count += 1

    return args_count


def _compile_CALL_MEMBER(process, compiler, code, node):
    obj = node.first()
    method = node.second()
    args = node.third()
    # print "_compile_LPAREN_MEMBER", obj, method, args

    args_count = _compile_args_list(process, compiler, code, args)

    _compile(process, compiler, code, obj)
    _emit_symbol_name(process, compiler, code, method.value)
    # TODO LITERAL HERE
    # declare_symbol(process, compiler,name)

    code.emit_1(CALL_METHOD, args_count, info(node))


def _compile_CALL(process, compiler, code, node):
    func = node.first()
    args = node.second()

    # print "_compile_LPAREN", func, args

    arg_count = _compile_args_list(process, compiler, code, args)

    _compile(process, compiler, code, func)

    code.emit_1(CALL, arg_count, info(node))


####
# MAIN SWITCH
####


def _compile(process, compiler, code, ast):
    if is_list_node(ast):
        _compile_nodes(process, compiler, code, ast)
    else:
        _compile_node(process, compiler, code, ast)


def _compile_nodes(process, compiler, code, ast):
    nodes = ast.items

    if len(nodes) > 1:
        for node in nodes[:-1]:
            _compile(process, compiler, code, node)
            _emit_pop(code)

    if len(nodes) > 0:
        node = nodes[-1]
        _compile(process, compiler, code, node)


def _compile_node(process, compiler, code, node):
    from obin.compile.parse.node import BaseNode
    if node is None:
        print None
    if is_list_node(node):
        print node
    if not isinstance(node, BaseNode):
        print node
    node_type = node.node_type
    if node_type is None:
        print 1

    assert node_type is not None

    if NT_TRUE == node_type:
        _compile_TRUE(process, compiler, code, node)
    elif NT_FALSE == node_type:
        _compile_FALSE(process, compiler, code, node)
    elif NT_NIL == node_type:
        _compile_NIL(process, compiler, code, node)
    elif NT_UNDEFINED == node_type:
        _compile_UNDEFINED(process, compiler, code, node)
    elif NT_INT == node_type:
        _compile_INT(process, compiler, code, node)
    elif NT_FLOAT == node_type:
        _compile_FLOAT(process, compiler, code, node)
    elif NT_STR == node_type:
        _compile_STR(process, compiler, code, node)
    elif NT_CHAR == node_type:
        _compile_CHAR(process, compiler, code, node)
    elif NT_NAME == node_type:
        _compile_NAME(process, compiler, code, node)
    elif NT_SPECIAL_NAME == node_type:
        _compile_SPECIAL_NAME(process, compiler, code, node)
    elif NT_SYMBOL == node_type:
        _compile_SYMBOL(process, compiler, code, node)

    elif NT_FUNC == node_type:
        _compile_FUNC(process, compiler, code, node)

    elif NT_IF == node_type:
        _compile_IF(process, compiler, code, node)
    elif NT_WHEN == node_type:
        _compile_WHEN(process, compiler, code, node)
    elif NT_MATCH == node_type:
        _compile_MATCH(process, compiler, code, node)
    elif NT_TRY == node_type:
        _compile_TRY(process, compiler, code, node)

    elif NT_IMPORT == node_type:
        _compile_IMPORT(process, compiler, code, node)
    elif NT_TRAIT == node_type:
        _compile_TRAIT(process, compiler, code, node)
    elif NT_ORIGIN == node_type:
        _compile_ORIGIN(process, compiler, code, node)
    elif NT_GENERIC == node_type:
        _compile_GENERIC(process, compiler, code, node)
    elif NT_SPECIFY == node_type:
        _compile_SPECIFY(process, compiler, code, node)

    elif NT_RETURN == node_type:
        _compile_RETURN(process, compiler, code, node)
    elif NT_THROW == node_type:
        _compile_THROW(process, compiler, code, node)

    elif NT_BREAK == node_type:
        _compile_BREAK(process, compiler, code, node)
    elif NT_CONTINUE == node_type:
        _compile_CONTINUE(process, compiler, code, node)
    elif NT_FOR == node_type:
        _compile_FOR(process, compiler, code, node)
    elif NT_WHILE == node_type:
        _compile_WHILE(process, compiler, code, node)

    elif NT_CALL == node_type:
        _compile_CALL(process, compiler, code, node)
    elif NT_CALL_MEMBER == node_type:
        _compile_CALL_MEMBER(process, compiler, code, node)

    elif NT_LIST == node_type:
        _compile_LIST(process, compiler, code, node)
    elif NT_TUPLE == node_type:
        _compile_TUPLE(process, compiler, code, node)
    elif NT_MAP == node_type:
        _compile_MAP(process, compiler, code, node)

    elif NT_LOOKUP == node_type:
        _compile_LOOKUP(process, compiler, code, node)
    elif NT_LOOKUP_SYMBOL == node_type:
        _compile_LOOKUP_SYMBOL(process, compiler, code, node)

    elif NT_CONS == node_type:
        _compile_CONS(process, compiler, code, node)
    elif NT_IN == node_type:
        _compile_IN(process, compiler, code, node)
    elif NT_IS == node_type:
        _compile_IS(process, compiler, code, node)
    elif NT_ISNOT == node_type:
        _compile_ISNOT(process, compiler, code, node)
    elif NT_AND == node_type:
        _compile_AND(process, compiler, code, node)
    elif NT_OR == node_type:
        _compile_OR(process, compiler, code, node)
    elif NT_NOT == node_type:
        _compile_NOT(process, compiler, code, node)
    elif NT_EQ == node_type:
        _compile_EQ(process, compiler, code, node)
    elif NT_LE == node_type:
        _compile_LE(process, compiler, code, node)
    elif NT_GE == node_type:
        _compile_GE(process, compiler, code, node)
    elif NT_NE == node_type:
        _compile_NE(process, compiler, code, node)
    elif NT_BITAND == node_type:
        _compile_BITAND(process, compiler, code, node)
    elif NT_BITNOT == node_type:
        _compile_BITNOT(process, compiler, code, node)
    elif NT_BITOR == node_type:
        _compile_BITOR(process, compiler, code, node)
    elif NT_BITXOR == node_type:
        _compile_BITXOR(process, compiler, code, node)
    elif NT_SUB == node_type:
        _compile_SUB(process, compiler, code, node)
    elif NT_ADD == node_type:
        _compile_ADD(process, compiler, code, node)
    elif NT_MUL == node_type:
        _compile_MUL(process, compiler, code, node)
    elif NT_DIV == node_type:
        _compile_DIV(process, compiler, code, node)
    elif NT_MOD == node_type:
        _compile_MOD(process, compiler, code, node)
    elif NT_LT == node_type:
        _compile_LT(process, compiler, code, node)
    elif NT_GT == node_type:
        _compile_GT(process, compiler, code, node)

    elif NT_RSHIFT == node_type:
        _compile_RSHIFT(process, compiler, code, node)
    elif NT_URSHIFT == node_type:
        _compile_URSHIFT(process, compiler, code, node)
    elif NT_LSHIFT == node_type:
        _compile_LSHIFT(process, compiler, code, node)

    elif NT_UNARY_PLUS == node_type:
        _compile_UNARY_PLUS(process, compiler, code, node)
    elif NT_UNARY_MINUS == node_type:
        _compile_UNARY_MINUS(process, compiler, code, node)

    elif NT_GOTO == node_type:
        _compile_GOTO(process, compiler, code, node)

    elif NT_ASSIGN == node_type:
        _compile_ASSIGN(process, compiler, code, node)
    elif NT_ADD_ASSIGN == node_type:
        _compile_ADD_ASSIGN(process, compiler, code, node)
    elif NT_SUB_ASSIGN == node_type:
        _compile_SUB_ASSIGN(process, compiler, code, node)
    elif NT_MUL_ASSIGN == node_type:
        _compile_MUL_ASSIGN(process, compiler, code, node)
    elif NT_DIV_ASSIGN == node_type:
        _compile_DIV_ASSIGN(process, compiler, code, node)
    elif NT_MOD_ASSIGN == node_type:
        _compile_MOD_ASSIGN(process, compiler, code, node)
    elif NT_BITAND_ASSIGN == node_type:
        _compile_BITAND_ASSIGN(process, compiler, code, node)
    elif NT_BITXOR_ASSIGN == node_type:
        _compile_BITXOR_ASSIGN(process, compiler, code, node)
    elif NT_BITOR_ASSIGN == node_type:
        _compile_BITOR_ASSIGN(process, compiler, code, node)
    else:
        compile_error(process, node, "Unknown node")


def newcode(compiler):
    return CodeSource(SourceInfo(compiler.source_path, compiler.source))


def compile_ast(process, compiler, ast):
    code = newcode(compiler)
    _enter_scope(process, compiler)
    _declare_arguments(process, compiler, None, False)
    _compile(process, compiler, code, ast)
    scope = _current_scope(process, compiler)
    final_scope = scope.finalize()
    compiled_code = code.finalize_compilation(final_scope)
    return compiled_code


def testprogram():
    with open("program2.obn") as f:
        data = f.read()

    return data


def compile(process, src, sourcename):
    ast = parse_string(src)
    # print ast
    compiler = Compiler(sourcename, src)
    code = compile_ast(process, compiler, ast)
    return code


def compile_module(process, modulename, src, sourcename):
    from obin.types.space import newmodule
    code = compile(process, src, sourcename)
    module = newmodule(process, modulename, code)
    return module


def compile_function_source(process, src, name):
    from obin.types.space import newfuncsource
    code = compile(process, src, name)
    fn = newfuncsource(name, code)
    return fn


def print_code(code):
    from code.utils import opcode_to_str
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
