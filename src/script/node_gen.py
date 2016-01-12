NODES = [
  "NT_TRUE",
  "NT_FALSE",
  "NT_NIL",
  "NT_UNDEFINED",
  "NT_INT",
  "NT_FLOAT",
  "NT_STR",
  "NT_CHAR",
  "NT_WILDCARD",
  "NT_NAME",
  "NT_SPECIAL_NAME",

  "NT_FUNC",

  "NT_IF",
  "NT_WHEN",
  "NT_MATCH",

  "NT_ORIGIN",
  "NT_IMPORT",
  "NT_TRAIT",
  "NT_GENERIC",
  "NT_SPECIFY",

  "NT_RETURN",
  "NT_THROW",

  "NT_BREAK",
  "NT_CONTINUE",
  "NT_FOR",
  "NT_WHILE",

  "NT_REST",

  "NT_MAP",
  "NT_COMMA",
  "NT_ASSIGN",
  "NT_CALL",
  "NT_CALL_FROM",
  "NT_LIST",
  "NT_TUPLE",
  "NT_LPAREN",
  "NT_LOOKUP",
  "NT_LOOKUP_SYMBOL",

  "NT_CONS",

  "NT_OF",
  "NT_AS",
  "NT_IN",
  "NT_IS",
  "NT_ISNOT",

  "NT_AND",
  "NT_OR",
  "NT_NOT",
  "NT_EQ",
  "NT_LE",
  "NT_GE",
  "NT_NE",
  "NT_BITAND",
  "NT_BITNOT",
  "NT_BITOR",
  "NT_BITXOR",
  "NT_SUB",
  "NT_ADD",
  "NT_MUL",
  "NT_DIV",
  "NT_MOD",
  "NT_LT",
  "NT_GT",
  "NT_RSHIFT",
  "NT_URSHIFT",
  "NT_LSHIFT",

  "NT_ADD_ASSIGN",
  "NT_SUB_ASSIGN",
  "NT_MUL_ASSIGN",
  "NT_DIV_ASSIGN",
  "NT_MOD_ASSIGN",
  "NT_BITAND_ASSIGN",
  "NT_BITXOR_ASSIGN",
  "NT_BITOR_ASSIGN",
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
print "def node_type_to_str(ttype):"
print "    return __NT_REPR__[ttype]"

    

# print "# ************************ COMPILE SWITCH*****************************"
# for number, token in enumerate(NODES):
#     t_str = token[0].replace("TT_", "")
#     print "    elif %s == t:" % token[0]
#     print "        self._compile_%s(code, node)" % t_str

