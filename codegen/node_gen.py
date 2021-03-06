from tpl import render

NODES = [
  # internals
  "NT_GOTO",

  # code nodes
  "NT_TRUE",
  "NT_FALSE",
  "NT_VOID",
  "NT_INT",
  "NT_FLOAT",
  "NT_STR",
  "NT_MULTI_STR",
  "NT_CHAR",
  "NT_WILDCARD",
  "NT_NAME",
  "NT_TEMPORARY",
  "NT_SYMBOL",

  "NT_TYPE",
  "NT_MAP",
  "NT_LIST",
  "NT_TUPLE",
  "NT_INDEXED",
  "NT_UNIT",
  "NT_CONS",
  "NT_COMMA",
  "NT_CASE",

  "NT_LENSE",

  "NT_LITERAL",

  "NT_FUN",
  "NT_DEF",
  "NT_OVERRIDE",
  "NT_USE",
  "NT_LAMBDA",

  "NT_DISPATCH",

  "NT_FARGS",

  "NT_CONDITION",
  "NT_WHEN",
  "NT_MATCH",
  "NT_TRY",
  "NT_RECEIVE",
  "NT_DECORATOR",

  "NT_MODULE",
  "NT_IMPORT",
  "NT_IMPORT_HIDING",
  "NT_INCLUDE",
  "NT_INCLUDE_HIDING",
  "NT_EXPORT",
  "NT_LOAD",
  "NT_TRAIT",
  "NT_EXTEND",
  "NT_GENERIC",
  "NT_METHOD",
  "NT_INTERFACE",
  "NT_DESCRIBE",

  "NT_BIND",

  "NT_THROW",

  "NT_REST",
  "NT_ASSIGN",
  "NT_ASSIGN_FORCE",
  "NT_CALL",
  "NT_JUXTAPOSITION",

  "NT_UNDEFINE",

  "NT_LOOKUP",
  "NT_IMPORTED_NAME",

  "NT_HEAD",
  "NT_TAIL",
  "NT_DROP",
  "NT_RANGE",

  "NT_MODIFY",

  "NT_OF",
  "NT_IS_IMPLEMENTED",
  "NT_AS",
  "NT_DELAY",
  "NT_LET",

  "NT_NOT",
  "NT_AND",
  "NT_OR",

  "NT_END_EXPR",
  "NT_END",
]





## FOR PYTHON LEXER
print "# ************************ OBIN NODES*****************************"
for number, token in enumerate(NODES):
    print "%s = %d" % (token, number)


print "# ************************ OBIN NODES REPR *****************************"
S = "__NT_REPR__ = ["
for name in NODES:
    S += "%s, " % str(("\"%s\"" % name))
S += "]"
print S
print
print
print "def node_type_to_s(ntype):"
print "    return __NT_REPR__[ntype]"

# print "# ************************ OBIN NODES MAPPING *****************************"
# for name in NODES:
#     print "%s: %s," % (name.replace("NT_", "TT_"), name)


# print "# ************************ COMPILE SWITCH*****************************"
# for number, node in enumerate(NODES):
#     n_str = node.replace("NT_", "")
#     print "    elif %s == node_type:" % node
#     print "        _compile_%s(process, compiler, code, node)" % n_str

