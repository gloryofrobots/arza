TOKENS = [
  ("TT_ENDSTREAM", None,),
  ("TT_INT", None,),
  ("TT_FLOAT", None,),
  ("TT_STR", None,),
  ("TT_CHAR", None,),
  ("TT_NAME", None),
  ("TT_OPERATOR", None),
  ("TT_NEWLINE", None,),

  ("TT_BREAK", "break"),
  ("TT_CASE", "case"),
  ("TT_CONTINUE", "continue"),
  ("TT_ELSE", "else"),
  ("TT_FOR", "for"),
  ("TT_WHILE", "while"),
  ("TT_IF", "if"),
  ("TT_WHEN", "when"),
  ("TT_ELIF", "elif"),
  ("TT_OF", "of"),
  ("TT_AS", "as"),
  ("TT_MATCH", "match"),
  ("TT_DEF", "def"),
  ("TT_FUN", "fun"),
  ("TT_VAR", "var"),
  ("TT_LAZY", "lazy"),
  ("TT_AND", "and"),
  ("TT_OR", "or"),
  ("TT_TRUE", "true"),
  ("TT_FALSE", "false"),
  ("TT_NIL", "nil"),
  ("TT_TRY", "try"),
  ("TT_THROW", "throw"),
  ("TT_CATCH", "catch"),
  ("TT_FINALLY", "finally"),
  ("TT_MODULE", "module"),
  ("TT_IMPORT", "import"),
  ("TT_EXPORT", "export"),
  ("TT_LOAD", "load"),
  ("TT_USE", "use"),
  ("TT_TRAIT", "trait"),
  ("TT_GENERIC", "generic"),
  ("TT_SPECIFY", "specify"),
  ("TT_END", "end"),
  ("TT_RETURN", "return"),
  ("TT_ISA", "isa"),
  ("TT_NOTA", "nota"),
  ("TT_KINDOF", "kindof"),
  ("TT_IN", "in"),
  ("TT_IS", "is"),
  ("TT_ISNOT", "isnot"),
  ("TT_NOTIN", "notin"),
  ("TT_NOT", "not"),


  ("TT_ELLIPSIS", "..."),
  ("TT_WILDCARD", "_"),
  ("TT_GOTO", "goto"),
  ("TT_ARROW", "->"),
  ("TT_AT_SIGN", "@"),
  

  ("TT_SEMI", ";"),
  ("TT_SHARP", "#"),

  ("TT_LCURLY", "{"),
  ("TT_RCURLY", "}"),
  ("TT_COMMA", ","),
  ("TT_ASSIGN", "="),
  ("TT_LPAREN", "("),
  ("TT_RPAREN", ")"),
  ("TT_LSQUARE", "["),
  ("TT_RSQUARE", "]"),
  ("TT_DOT", "."),
  ("TT_DOUBLE_DOT", ".."),
  # ("TT_BACKTICK", "`"),
  ("TT_UNKNOWN", None)
]

"""
print "********************************ENUM********************************"
for number, token in enumerate(TOKENS):
  print "    %s = %d," % (token[0],number)

print "****************************TOSTRING***********************************"
for name,pattern in TOKENS:
  print "    case %s: return \"%s\";" % (name, name)

print "************************PATTERNS*****************************"
for name,pattern in TOKENS:
    if pattern:
        print "\"%s\" { return %s; }" % (pattern, name)

"""
## FOR PYTHON LEXER
print "# ************************ OBIN TOKENS*****************************"
for number, token in enumerate(TOKENS):
    print "%s = %d" % (token[0],number)
    
  
print "# ************************ OBIN TOKENS REPR *****************************"
S = "__TT_REPR__ = ["
for name,pattern in TOKENS:
    S += "%s, " % str(("u\"%s\"" % name))
S += "]"
print S
print 
print 
print "def token_type_to_str(ttype):"
print "    return __TT_REPR__[ttype]"


# print "# ************************ COMPILE SWITCH*****************************"
# for number, token in enumerate(TOKENS):
#     t_str = token[0].replace("TT_", "")
#     print "    elif %s == t:" % token[0]
#     print "        self._compile_%s(code, node)" % t_str

