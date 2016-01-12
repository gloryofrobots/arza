__author__ = 'gloryofrobots'
from obin.compile.parse.node import (is_empty_node, is_list_node, is_iterable_node, create_tuple_node)
from obin.compile.parse.parser import *
from obin.compile.scope import Scope
from obin.objects import space as obs
from obin.objects import api
from obin.builtins.internals import internals
from obin.compile.code.source import CodeSource
from obin.compile.code import *
from obin.utils.misc import is_absent_index
from obin.compile.parse.token_type import *


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
    def __init__(self):
        self.property_funclists = []
        self.property_scopes = []
        self.property_sourcename = ""
        self.property_depth = -1


########################
# SCOPES
########################


def _enter_scope(process, compiler):
    compiler.property_depth = compiler.property_depth + 1

    new_scope = Scope()
    compiler.property_scopes.append(new_scope)
    # print 'starting new scope %d' % (process, compiler.depth, )


def _is_modifiable_binding(process, compiler, name):
    scope = _current_scope(process, compiler)
    if not is_absent_index(scope.get_local_index(name)):
        return True
    if scope.has_outer(name):
        return True

    return False


def _declare_outer(process, compiler, symbol):
    scope = _current_scope(process, compiler)
    if not scope.is_function_scope():
        compile_error_1(process, compiler.current_node,
                        "Outer variables can be declared only inside functions", symbol)
    if scope.has_outer(symbol):
        compile_error_1(process, compiler.current_node, "Outer variable has already been declared", symbol)
    scope.add_outer(symbol)


# def declare_symbol(process, compiler, symbol):
#     assert obs.isstring(symbol)
#     idx = scopes[-1].add_symbol(process, compiler,symbol)
#     # print "SYMBOL", symbol, len(symbol), idx
#     return idx

def _declare_arguments(process, compiler, args, varargs):
    _current_scope(process, compiler).add_arguments(args, varargs)


def _declare_function_name(process, compiler, name):
    _current_scope(process, compiler).add_function_name(name)


def _declare_reference(process, compiler, symbol):
    assert obs.isstring(symbol)
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
    assert api.n_length(symbol) > 0
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
    for scope in reversed(compiler.property_scopes):
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
    compiler.property_depth = compiler.property_depth - 1
    compiler.property_scopes.pop()
    # print 'closing scope, returning to %d' % (process, compiler.depth, )


def _current_scope(process, compiler):
    return compiler.property_scopes[-1]


"""
    HOOKS
"""


def _compile_FLOAT(process, compiler, bytecode, node):
    value = float(node.value)
    idx = _declare_literal(process, compiler, obs.newfloat(value))
    bytecode.emit_1(LITERAL, idx)


def _compile_INT(process, compiler, bytecode, node):
    value = int(node.value)
    _emit_integer(process, compiler, bytecode, value)


def _emit_integer(process, compiler, bytecode, integer):
    idx = _declare_literal(process, compiler, obs.newint(integer))
    bytecode.emit_1(LITERAL, idx)


def _compile_TRUE(process, compiler, bytecode, node):
    bytecode.emit_0(TRUE)


def _compile_FALSE(process, compiler, bytecode, node):
    bytecode.emit_0(FALSE)


def _compile_NIL(process, compiler, bytecode, node):
    bytecode.emit_0(NULL)


def _compile_UNDEFINED(process, compiler, bytecode, node):
    bytecode.emit_0(UNDEFINED)


def _emit_string_name(process, compiler, bytecode, name):
    string = obs.newstring_from_str(name.value)
    return _emit_string(process, compiler, bytecode, string)


def _emit_string(process, compiler, bytecode, string):
    idx = _declare_literal(process, compiler, string)
    bytecode.emit_1(LITERAL, idx)
    return idx


def _compile_STR(process, compiler, bytecode, node):
    from obin.runistr import unicode_unescape, decode_str_utf8

    strval = str(node.value)
    strval = decode_str_utf8(strval)
    strval = string_unquote(strval)
    strval = unicode_unescape(strval)
    _emit_string(process, compiler, bytecode, obs.newstring(strval))


def _compile_CHAR(process, compiler, bytecode, node):
    from obin.runistr import unicode_unescape, decode_str_utf8

    strval = str(node.value)
    strval = decode_str_utf8(strval)
    strval = string_unquote(strval)
    strval = unicode_unescape(strval)
    _emit_string(process, compiler, bytecode, obs.newstring(strval))


def _compile_OUTER(process, compiler, bytecode, node):
    assert False, "Why you need it?"
    name = obs.newstring_from_str(node.first().value)
    _declare_outer(process, compiler, name)


def _on_binary_primitive(process, compiler, code, node, name):
    _compile(process, compiler, code, node.first())
    _compile(process, compiler, code, node.second())
    code.emit_1(CALL_INTERNAL, name)


def _on_unary_primitive(process, compiler, code, node, name):
    _compile(process, compiler, code, node.first())
    code.emit_1(CALL_INTERNAL, name)


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


def _compile_AND(process, compiler, bytecode, node):
    _compile(process, compiler, bytecode, node.first())
    one = bytecode.prealocate_label()
    bytecode.emit_1(JUMP_IF_FALSE_NOPOP, one)
    _compile(process, compiler, bytecode, node.second())
    bytecode.emit_1(LABEL, one)


def _compile_OR(process, compiler, bytecode, node):
    _compile(process, compiler, bytecode, node.first())
    one = bytecode.prealocate_label()
    bytecode.emit_1(JUMP_IF_TRUE_NOPOP, one)
    _compile(process, compiler, bytecode, node.second())
    bytecode.emit_1(LABEL, one)


def _compile_ASSIGN_MEMBER(process, compiler, bytecode, node):
    member = node.first()
    value = node.second()
    obj = member.first()
    item = member.second()

    _compile(process, compiler, bytecode, value)
    _compile(process, compiler, bytecode, item)
    _compile(process, compiler, bytecode, obj)
    bytecode.emit_0(STORE_MEMBER)


def _compile_ASSIGN_SYMBOL(process, compiler, bytecode, node):
    member = node.first()
    name = obs.newstring_from_str(member.second().value)

    obj = member.first()
    _compile(process, compiler, bytecode, node.second())
    _emit_string(process, compiler, bytecode, name)
    _compile(process, compiler, bytecode, obj)
    bytecode.emit_0(STORE_MEMBER)


def _emit_store(process, compiler, bytecode, name):
    index, is_local = _declare_variable(process, compiler, name)
    name_index = _declare_literal(process, compiler, name)
    if is_local:
        bytecode.emit_2(STORE_LOCAL, index, name_index)
    else:
        bytecode.emit_2(STORE_OUTER, index, name_index)


def _emit_store_n_string(process, compiler, bytecode, namestring):
    name = obs.newstring_from_str(namestring)
    _emit_store(process, compiler, bytecode, name)


def _emit_store_name(process, compiler, bytecode, namenode):
    _emit_store_n_string(process, compiler, bytecode, namenode.value)


#########################################################

PATTERN_DATA = """
    match (1, 2):
        case (Z, 1): 12 + Z end
        case (1, 2): 11 end

        case (1, Z, B, 1): 12 + Z end
        case (1, Z, Y, A):  Z + Y + A   end
        //case (1, x): 1 + 1 end
        //case (1, false): 2 end
        //case (34.05, 42, y): 3 end
        //case (34.05, 42, (w,z)): 4 end
         case _: nil end
        // case A: 5 end
    end
"""


def _compile_MATCH(process, compiler, code, node):
    from obin.compile.match import transform
    from obin.compile.parse.node import create_goto_node
    from obin.compile import MATCH_SYS_VAR
    exp = node.first()
    patterns = node.second()

    name = obs.newstring_from_str(MATCH_SYS_VAR)
    index = _declare_local(process, compiler, name)
    name_index = _declare_literal(process, compiler, name)
    _compile(process, compiler, code, exp)
    code.emit_2(STORE_LOCAL, index, name_index)

    endmatch = code.prealocate_label()
    graph = transform(process, compiler, node, patterns, create_goto_node(endmatch))
    _compile(process, compiler, code, graph)
    code.emit_1(LABEL, endmatch)


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
    code.emit_1(JUMP, value)


#########################################################
#####
# DESTRUCT DESTRUCT
####
def _compile_destruct(process, compiler, bytecode, node):
    _compile(process, compiler, bytecode, node.second())
    return _compile_destruct_recur(process, compiler, bytecode, node.first())


def _is_optimizable_unpack_seq_pattern(node):
    items = node.first()
    for child in items:
        if child is None:
            print ""
        if child.node_type != NT_NAME:
            return False
    return True


def _compile_destruct_recur(process, compiler, bytecode, node):
    if node.node_type == NT_TUPLE:
        # x,y,z = foo() optimisation to single unpack opcode
        if _is_optimizable_unpack_seq_pattern(node):
            return _compile_destruct_unpack_seq(process, compiler, bytecode, node)
        else:
            return _compile_destruct_recur_seq(process, compiler, bytecode, node)
    elif node.node_type == NT_MAP:
        return _compile_destruct_recur_table(process, compiler, bytecode, node)
    else:
        compile_error(process, node, "unsupported assignment syntax")


def _compile_destruct_recur_table(process, compiler, bytecode, node):
    pairs = node.first()
    for pair in pairs:
        bytecode.emit_0(DUP)

        key = pair[0]
        value = pair[1]
        varname = None
        if is_empty_node(value):
            varname = key
        elif value.node_type == NT_NAME:
            varname = value

        _emit_map_key(process, compiler, bytecode, key)

        bytecode.emit_0(MEMBER)

        if varname is None:
            _compile_destruct_recur(process, compiler, bytecode, value)
            bytecode.emit_0(POP)
        else:
            _emit_store_name(process, compiler, bytecode, varname)
            bytecode.emit_0(POP)


##################################################
# DESTRUCT SEQUENCE
##################################################

def _compile_destruct_recur_seq_rest(process, compiler, bytecode, last_item, last_index):
    bytecode.emit_0(DUP)
    varname = last_item.first()
    _emit_integer(process, compiler, bytecode, last_index)
    bytecode.emit_0(UNDEFINED)
    bytecode.emit_0(SLICE)
    _emit_store_name(process, compiler, bytecode, varname)
    bytecode.emit_0(POP)


def _compile_destruct_recur_seq_item(process, compiler, bytecode, item, index):
    bytecode.emit_0(DUP)

    varname = None
    if item.node_type == NT_NAME:
        varname = item

    idx = _declare_literal(process, compiler, obs.newint(index))
    bytecode.emit_1(LITERAL, idx)
    bytecode.emit_0(MEMBER)

    if varname is None:
        _compile_destruct_recur(process, compiler, bytecode, item)
        bytecode.emit_0(POP)
    else:
        _emit_store_name(process, compiler, bytecode, varname)
        bytecode.emit_0(POP)


def _compile_destruct_recur_seq(process, compiler, bytecode, node):
    items = node.first()
    length = len(items)

    last_index = length - 1

    for i in range(last_index):
        item = items[i]
        _compile_destruct_recur_seq_item(process, compiler, bytecode, item, i)

    last_item = items[last_index]
    if last_item.node_type == NT_REST:
        _compile_destruct_recur_seq_rest(process, compiler, bytecode, last_item, last_index)
    else:
        _compile_destruct_recur_seq_item(process, compiler, bytecode, last_item, last_index)


def _compile_destruct_unpack_seq(process, compiler, bytecode, node):
    bytecode.emit_0(DUP)
    names = node.first()
    length = len(names)
    bytecode.emit_1(UNPACK_SEQUENCE, length)
    for name in names[0:-1]:
        _emit_store_name(process, compiler, bytecode, name)
        bytecode.emit_0(POP)
    last_name = names[-1]
    _emit_store_name(process, compiler, bytecode, last_name)
    bytecode.emit_0(POP)


################################################################################

def _compile_ASSIGN(process, compiler, bytecode, node):
    left = node.first()
    if left.node_type == NT_LOOKUP_SYMBOL:
        return _compile_ASSIGN_SYMBOL(process, compiler, bytecode, node)
    elif left.node_type == NT_LOOKUP:
        return _compile_ASSIGN_MEMBER(process, compiler, bytecode, node)
    elif left.node_type == NT_TUPLE or left.node_type == NT_MAP:
        return _compile_destruct(process, compiler, bytecode, node)

    _compile(process, compiler, bytecode, node.second())
    name = obs.newstring_from_str(left.value)
    _emit_store(process, compiler, bytecode, name)


def _compile_modify_assignment_dot_primitive(process, compiler, bytecode, node, operation):
    member = node.first()
    name = obs.newstring_from_str(member.second().value)

    obj = member.first()

    _compile(process, compiler, bytecode, node.first())
    _compile(process, compiler, bytecode, node.second())
    bytecode.emit_1(CALL_INTERNAL, operation)

    # _compile(process, compiler,bytecode, node.second())
    _emit_string(process, compiler, bytecode, name)
    _compile(process, compiler, bytecode, obj)
    bytecode.emit_0(STORE_MEMBER)


def _compile_modify_assignment_primitive(process, compiler, bytecode, node, operation):
    left = node.first()
    if left.node_type == NT_LOOKUP_SYMBOL:
        return _compile_modify_assignment_dot_primitive(process, compiler, bytecode, node, operation)

    name = obs.newstring_from_str(left.value)
    if not _is_modifiable_binding(process, compiler, name):
        compile_error_1(process, node, "Unreachable variable", name)

    # _compile(process, compiler,bytecode, left)
    _compile(process, compiler, bytecode, node.first())
    _compile(process, compiler, bytecode, node.second())
    bytecode.emit_1(CALL_INTERNAL, operation)
    _emit_store(process, compiler, bytecode, name)


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
    if node.node_type == NT_SPECIAL_NAME:
        name_value = _get_special_name_value(process, compiler, node)
    elif node.node_type == NT_NAME:
        name_value = node.value
    else:
        return compile_error(process, node, "Invalid node in lookup")

    name = obs.newstring_from_str(name_value)
    _compile_name_lookup(process, compiler, code, name)


def _compile_name_lookup(process, compiler, code, name):
    index, is_local = _get_variable_index(process, compiler, name)
    name_index = _declare_literal(process, compiler, name)
    if is_local:
        code.emit_2(LOCAL, index, name_index)
    else:
        code.emit_2(OUTER, index, name_index)


def _get_special_name_value(process, compiler, node):
    return node.value[1:len(node.value) - 1]


def _compile_SPECIAL_NAME(process, compiler, code, node):
    name = obs.newstring_from_str(_get_special_name_value(process, compiler, node))
    _compile_name_lookup(process, compiler, code, name)


def _compile_NAME(process, compiler, code, node):
    _compile_node_name_lookup(process, compiler, code, node)


def _compile_RETURN(process, compiler, code, node):
    expr = node.first()
    if is_empty_node(expr):
        code.emit_0(UNDEFINED)
    else:
        _compile(process, compiler, code, expr)

    code.emit_0(RETURN)


def _compile_THROW(process, compiler, code, node):
    expr = node.first()
    if is_empty_node(expr):
        code.emit_0(UNDEFINED)
    else:
        _compile(process, compiler, code, expr)

    code.emit_0(THROW)


def _emit_map_key(process, compiler, code, key):
    if key.node_type == NT_NAME:
        # in case of names in object literal we must convert them to strings
        _emit_string_name(process, compiler, code, key)
    else:
        _compile(process, compiler, code, key)


def _compile_map(process, compiler, code, items):
    for c in items:
        key = c[0]
        value = c[1]
        if is_empty_node(value):
            _compile_NIL(process, compiler, code, value)
        else:
            _compile(process, compiler, code, value)

        _emit_map_key(process, compiler, code, key)

    code.emit_1(MAP, len(items))


def _compile_MAP(process, compiler, code, node):
    items = node.first()
    _compile_map(process, compiler, code, items)


def _compile_TUPLE(process, compiler, code, node):
    items = node.first()
    for c in items:
        _compile(process, compiler, code, c)

    code.emit_1(TUPLE, len(items))


def _compile_LIST(process, compiler, code, node):
    items = node.first()
    for c in items:
        _compile(process, compiler, code, c)

    code.emit_1(LIST, len(items))


# def _emit_list(process, compiler, code, node):
#     items = node.first()
#
#     for c in items:
#         _compile(process, compiler, code, c)
#
#     code.emit_1(LIST, len(items))


def _compile_BREAK(process, compiler, code, node):
    code.emit_0(UNDEFINED)
    if not code.emit_break():
        compile_error(process, node, "break outside loop")


def _compile_CONTINUE(process, compiler, code, node):
    code.emit_0(UNDEFINED)
    if not code.emit_continue():
        compile_error(process, node, "continue outside loop")


def _compile_func_args_and_body(process, compiler, code, funcname, params, outers, body, opcode):
    _enter_scope(process, compiler)

    funccode = CodeSource()

    if is_empty_node(params):
        _declare_arguments(process, compiler, None, None)
    else:
        args = params.first()
        length = args.length()
        funccode.emit_0(ARGUMENTS)

        _declare_arguments(process, compiler, [obs.newstring(u"$%d" % i) for i in range(length)], None)
        _compile_destruct_recur(process, compiler, funccode, params)

    if is_iterable_node(outers):
        for outer in outers:
            _declare_outer(process, compiler, obs.newstring_from_str(outer.value))

    # avoid recursive name lookups for origins because in this case
    # index will be pointed to constructor function instead of origin
    if not funcname.isempty() and not opcode == ORIGIN:
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
    code.emit_1(opcode, source_index)


def _compile_FUNC(process, compiler, code, node):
    name = node.first()
    if not is_empty_node(name):
        funcname = obs.newstring_from_str(name.value)
    else:
        funcname = obs.newstring(u"")

    params = node.second()
    outers = node.third()
    body = node.fourth()
    _compile_func_args_and_body(process, compiler, code, funcname, params, outers, body, FUNCTION)

    if funcname.isempty():
        return

    index = _declare_local(process, compiler, funcname)
    funcname_index = _declare_literal(process, compiler, funcname)
    code.emit_2(STORE_LOCAL, index, funcname_index)


def _compile_ORIGIN(process, compiler, code, node):
    name = node.first()
    funcname = obs.newstring_from_str(name.value)
    index = _declare_local(process, compiler, funcname)

    params = node.second()
    outers = node.third()
    body = node.fourth()
    _compile_func_args_and_body(process, compiler, code, funcname, params, outers, body, ORIGIN)

    funcname_index = _declare_literal(process, compiler, funcname)
    code.emit_2(STORE_LOCAL, index, funcname_index)


def _compile_branch(process, compiler, bytecode, condition, body, endif):
    _compile(process, compiler, bytecode, condition)
    end_body = bytecode.prealocate_label()
    bytecode.emit_1(JUMP_IF_FALSE, end_body)
    _compile(process, compiler, bytecode, body)
    bytecode.emit_1(JUMP, endif)
    bytecode.emit_1(LABEL, end_body)


def _compile_WHEN(process, compiler, code, node):
    condition = node.first()
    truebranch = node.second()
    falsebranch = node.third()
    endif = code.prealocate_label()
    _compile_branch(process, compiler, code, condition, truebranch, endif)
    _compile(process, compiler, code, falsebranch)
    code.emit_1(LABEL, endif)


def _compile_IF(process, compiler, code, node):
    branches = node.first()

    endif = code.prealocate_label()

    for i in range(len(branches) - 1):
        branch = branches[i]
        _compile_branch(process, compiler, code, branch[0], branch[1], endif)

    elsebranch = branches[-1]
    if is_empty_node(elsebranch):
        code.emit_0(UNDEFINED)
    else:
        _compile(process, compiler, code, elsebranch[1])

    code.emit_1(LABEL, endif)


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
    code.emit_1(IMPORT, module_path_literal)

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
    code.emit_1(IMPORT, module_path_literal)


def _compile_IMPORT(process, compiler, code, node):
    if node.arity == 2:
        _compile_IMPORT_STMT(process, compiler, code, node)
    else:
        _compile_IMPORT_EXP(process, compiler, code, node)


def _compile_GENERIC(process, compiler, code, node):
    name_node = node.first()
    if name_node.node_type == NT_SPECIAL_NAME:
        name_value = _get_special_name_value(process, compiler, name_node)
    else:
        name_value = name_node.value

    name = obs.newstring_from_str(name_value)

    index = _declare_local(process, compiler, name)
    name_index = _declare_literal(process, compiler, name)
    code.emit_1(GENERIC, name_index)
    code.emit_2(STORE_LOCAL, index, name_index)

    if node.arity == 2:
        methods = node.second()
        _emit_specify(process, compiler, code, node, methods)


def _compile_TRAIT(process, compiler, code, node):
    name = node.first()
    name = obs.newstring_from_str(name.value)
    index = _declare_local(process, compiler, name)
    name_index = _declare_literal(process, compiler, name)
    code.emit_1(TRAIT, name_index)
    code.emit_2(STORE_LOCAL, index, name_index)


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
                code.emit_0(UNDEFINED)
            else:
                _compile(process, compiler, code, trait)

        code.emit_1(TUPLE, len(signature))

        method_name = obs.newstring(u"")
        args_node = create_tuple_node(node, args)
        _compile_func_args_and_body(process, compiler, code, method_name, args_node, empty_node(),
                                    method_body,
                                    FUNCTION)
        code.emit_1(TUPLE, 2)

    code.emit_1(SPECIFY, len(methods))


def _compile_SPECIFY(process, compiler, code, node):
    name = node.first()
    _compile_node_name_lookup(process, compiler, code, name)
    methods = node.second()
    _emit_specify(process, compiler, code, node, methods)


def _compile_FOR(process, compiler, bytecode, node):
    vars = node.first()
    name = obs.newstring_from_str(vars[0].value)

    source = node.second()
    body = node.third()
    _compile(process, compiler, bytecode, source)
    bytecode.emit_0(ITERATOR)
    # load the "last" iterations result
    bytecode.emit_0(UNDEFINED)
    precond = bytecode.emit_startloop_label()
    bytecode.continue_at_label(precond)
    finish = bytecode.prealocate_endloop_label(False)
    # update = bytecode.prealocate_updateloop_label()

    bytecode.emit_1(JUMP_IF_ITERATOR_EMPTY, finish)

    # put next iterator value on stack
    bytecode.emit_0(NEXT)

    index = _declare_local(process, compiler, name)
    # _compile_string(process, compiler,bytecode, name)
    name_index = _declare_literal(process, compiler, name)
    bytecode.emit_2(STORE_LOCAL, index, name_index)
    bytecode.emit_0(POP)

    _compile(process, compiler, bytecode, body)
    # bytecode.emit_updateloop_label(update)

    bytecode.emit_1(JUMP, precond)
    bytecode.emit_endloop_label(finish)


def _compile_WHILE(process, compiler, bytecode, node):
    condition = node.first()
    body = node.second()
    bytecode.emit_0(UNDEFINED)
    startlabel = bytecode.emit_startloop_label()
    bytecode.continue_at_label(startlabel)
    _compile(process, compiler, bytecode, condition)
    endlabel = bytecode.prealocate_endloop_label()
    bytecode.emit_1(JUMP_IF_FALSE, endlabel)
    bytecode.emit_0(POP)
    _compile(process, compiler, bytecode, body)
    bytecode.emit_1(JUMP, startlabel)
    bytecode.emit_endloop_label(endlabel)
    bytecode.done_continue()


def _compile_CONS(process, compiler, code, node):
    _on_binary_primitive(process, compiler, code, node, internals.CONS)


def _compile_LOOKUP_SYMBOL(process, compiler, code, node):
    obj = node.first()
    _compile(process, compiler, code, obj)
    name = obs.newstring_from_str(node.second().value)
    _emit_string(process, compiler, code, name)
    code.emit_0(MEMBER)


def _compile_LOOKUP(process, compiler, code, node):
    # TODO OPTIMISATION FOR INDEX LOOKUP
    obj = node.first()
    _compile(process, compiler, code, obj)
    expr = node.second()
    _compile(process, compiler, code, expr)
    code.emit_0(MEMBER)


def _compile_args_list(process, compiler, code, args):
    args_count = 0

    for arg in args:
        _compile(process, compiler, code, arg)
        args_count += 1

    return args_count


def _compile_CALL_MEMBER(process, compiler, bytecode, node):
    obj = node.first()
    method = node.second()
    name = obs.newstring_from_str(method.value)
    args = node.third()
    # print "_compile_LPAREN_MEMBER", obj, method, args

    args_count = _compile_args_list(process, compiler, bytecode, args)

    _compile(process, compiler, bytecode, obj)
    _emit_string(process, compiler, bytecode, name)
    # TODO LITERAL HERE
    # declare_symbol(process, compiler,name)

    bytecode.emit_1(CALL_METHOD, args_count)


def _compile_CALL(process, compiler, bytecode, node):
    func = node.first()
    args = node.second()

    # print "_compile_LPAREN", func, args

    arg_count = _compile_args_list(process, compiler, bytecode, args)

    _compile(process, compiler, bytecode, func)

    bytecode.emit_1(CALL, arg_count)


####
# MAIN SWITCH
####


def _compile(process, compiler, code, ast):
    if is_list_node(ast):
        _compile_nodes(process, compiler, code, ast)
    else:
        _compile_node(process, compiler, code, ast)


def _compile_nodes(process, compiler, bytecode, ast):
    nodes = ast.items

    if len(nodes) > 1:
        for node in nodes[:-1]:
            _compile(process, compiler, bytecode, node)
            bytecode.emit_0(POP)

    if len(nodes) > 0:
        node = nodes[-1]
        _compile(process, compiler, bytecode, node)


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
    elif NT_FUNC == node_type:
        _compile_FUNC(process, compiler, code, node)
    elif NT_IF == node_type:
        _compile_IF(process, compiler, code, node)
    elif NT_WHEN == node_type:
        _compile_WHEN(process, compiler, code, node)
    elif NT_MATCH == node_type:
        _compile_MATCH(process, compiler, code, node)
    elif NT_ORIGIN == node_type:
        _compile_ORIGIN(process, compiler, code, node)
    elif NT_IMPORT == node_type:
        _compile_IMPORT(process, compiler, code, node)
    elif NT_TRAIT == node_type:
        _compile_TRAIT(process, compiler, code, node)
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
    elif NT_MAP == node_type:
        _compile_MAP(process, compiler, code, node)
    elif NT_ASSIGN == node_type:
        _compile_ASSIGN(process, compiler, code, node)
    elif NT_CALL == node_type:
        _compile_CALL(process, compiler, code, node)
    elif NT_CALL_MEMBER == node_type:
        _compile_CALL_MEMBER(process, compiler, code, node)
    elif NT_LIST == node_type:
        _compile_LIST(process, compiler, code, node)
    elif NT_TUPLE == node_type:
        _compile_TUPLE(process, compiler, code, node)
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
    elif NT_ADD_ASSIGN == node_type:
        _compile_ADD_ASSIGN(process, compiler, code, node)
    elif NT_GOTO == node_type:
        _compile_GOTO(process, compiler, code, node)
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


def compile_ast(process, compiler, ast):
    code = CodeSource()
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


def compile(process, src):
    ast = parse_string(src)
    # print ast
    compiler = Compiler()
    code = compile_ast(process, compiler, ast)
    return code


def compile_module(process, name, src):
    from obin.objects.space import newmodule
    code = compile(process, src)
    module = newmodule(process, name, code)
    return module


def compile_function_source(process, src, name):
    from obin.objects.space import newfuncsource
    code = compile(process, src)
    fn = newfuncsource(name, code)
    return fn


def print_code(code):
    from code.utils import opcode_to_str
    print "\n".join([str((opcode_to_str(c[0]), str(c[1:]))) for c in code.opcodes])


def compile_and_print(txt):
    print_code(compile(None, txt))


def _check(val1, val2):
    print val1
    print val2
    if val1 != val2:
        print val1
        print val2
        raise RuntimeError("Not equal")


# compile_and_print(
#     PATTERN_DATA
# )
"""

metadata = 34;

{
    title: englishTitle,
    subject,
    translationsUa: { title: localeTitle, translator },
    translationsEn: { titleEn: (localeTitle, origTitle), translator },
    author:author_data
} = metadata;


    specify fire {
        (self of Soldier, other of Civilian) {
            attack(self, other)
            name = self.name
            surname = "Surname" + name + other.name
        }
        (self of Soldier, other1, other2) {
            attack(self, other)
            name = self.name
            surname = "Surname" + name + other.name
        }
        (self, other1, other2, other3 of Enemy) {
            attack(self, other)
            name = self.name
            surname = "Surname" + name + other.name
        }
    }
"""

