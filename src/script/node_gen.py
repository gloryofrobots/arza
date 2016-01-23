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
  "NT_SYMBOL",

  "NT_FUNC",

  "NT_IF",
  "NT_WHEN",
  "NT_MATCH",
  "NT_TRY",

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
  "NT_ASSIGN",
  "NT_CALL",
  "NT_CALL_MEMBER",
  "NT_LIST",
  "NT_TUPLE",
  "NT_LOOKUP",
  "NT_LOOKUP_SYMBOL",
  "NT_SLICE",
  "NT_RANGE",
  "NT_MODIFY",
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
  "NT_UNARY_PLUS",
  "NT_UNARY_MINUS",

  "NT_GOTO",
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

# print "# ************************ OBIN NODES MAPPING *****************************"
# for name in NODES:
#     print "%s: %s," % (name.replace("NT_", "TT_"), name)
    

# print "# ************************ COMPILE SWITCH*****************************"
# for number, node in enumerate(NODES):
#     n_str = node.replace("NT_", "")
#     print "    elif %s == node_type:" % node
#     print "        _compile_%s(process, compiler, code, node)" % n_str
                  
