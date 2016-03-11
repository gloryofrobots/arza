from tpl import render

NODES = [
  # internals
  "NT_GOTO",

  # code nodes 
  "NT_TRUE",
  "NT_FALSE",
  "NT_INT",
  "NT_FLOAT",
  "NT_STR",
  "NT_CHAR",
  "NT_WILDCARD",
  "NT_NAME",
  "NT_SYMBOL",

  "NT_DERIVE",
  "NT_TYPE",
  "NT_MAP",
  "NT_LIST",
  "NT_TUPLE",
  "NT_UNIT",
  "NT_COMMA",

  "NT_FUN",

  "NT_FENV",

  "NT_CONDITION",
  "NT_TERNARY_CONDITION",
  "NT_WHEN",
  "NT_MATCH",
  "NT_TRY",

  "NT_MODULE",
  "NT_IMPORT",
  "NT_IMPORT_HIDING",
  "NT_IMPORT_FROM",
  "NT_IMPORT_FROM_HIDING",
  "NT_EXPORT",
  "NT_LOAD",
  "NT_TRAIT",
  "NT_IMPLEMENT",

  "NT_BIND",

  "NT_THROW",

  "NT_BREAK",
  "NT_CONTINUE",
  "NT_FOR",
  "NT_WHILE",

  "NT_REST",

  "NT_ASSIGN",
  "NT_CALL",
  "NT_JUXTAPOSITION",

  "NT_UNDEFINE",

  "NT_LOOKUP",
  "NT_LOOKUP_SYMBOL",
  "NT_LOOKUP_MODULE",
  
  "NT_HEAD",
  "NT_TAIL",
  "NT_DROP",
  "NT_RANGE",

  "NT_MODIFY",

  "NT_OF",
  "NT_AS",
  "NT_VAR",
  "NT_LAZY", 

  "NT_AND",
  "NT_OR",

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
                  
