TOKENS = [
  ("TT_ENDSTREAM", None,),
  ("TT_INT", None,),
  ("TT_FLOAT", None,),
  ("TT_STR", None,),
  ("TT_CHAR", None,),
  ("TT_NAME", None,),
  ("TT_NEWLINE", None,),

  ("TT_BREAK", "break"),
  ("TT_CASE", "case"),
  ("TT_CONTINUE", "continue"),
  ("TT_DO", "do"),
  ("TT_ELSE", "else"),
  ("TT_FOR", "for"),
  ("TT_WHILE", "while"),
  ("TT_IF", "if"),
  ("TT_WHEN", "when"),
  ("TT_ELIF", "elif"),
  ("TT_OF", "of"),
  ("TT_MATCH", "match"),
  ("TT_FN", "fn"),
  ("TT_AND", "and"),
  ("TT_OR", "or"),
  ("TT_NOT", "not"),
  ("TT_TRUE", "true"),
  ("TT_FALSE", "false"),
  ("TT_NIL", "nil"),
  ("TT_UNDEFINED", "undefined"),
  ("TT_RAISE", "raise"),
  ("TT_THEN", "then"),
  ("TT_YIELD", "yield"),
  ("TT_FROM", "from"),
  ("TT_IN", "in"),
  ("TT_IS", "is"),
  ("TT_OBJECT", "object"),
  ("TT_ISNOT", "isnot"),
  ("TT_OUTER", "outer"),
  ("TT_RETURN", "return"),
  ("TT_ELLIPSIS", "..."),
  ("TT_ADD_ASSIGN", "+="),
  ("TT_SUB_ASSIGN", "-="),
  ("TT_MUL_ASSIGN", "*="),
  ("TT_DIV_ASSIGN", "/="),
  ("TT_MOD_ASSIGN", "%="),
  ("TT_BITAND_ASSIGN", "&="),
  ("TT_BITXOR_ASSIGN", "^="),
  ("TT_BITOR_ASSIGN", "|="),

  ("TT_RSHIFT", ">>"),
  ("TT_URSHIFT", ">>>"),
  ("TT_LSHIFT", "<<"),
  ("TT_ARROW", "->"),
  ("TT_FAT_ARROW", "=>"),
  
  ("TT_EQ", "=="),

  ("TT_LE", "<="),
  ("TT_GE", ">="),
  ("TT_NE", "!="),
  ("TT_SEMI", ";"),
  ("TT_COLON", ":"),

  ("TT_LCURLY", "{"),
  ("TT_RCURLY", "}"),
  ("TT_COMMA", ","),
  ("TT_ASSIGN", "="),
  ("TT_LPAREN", "("),
  ("TT_RPAREN", ")"),
  ("TT_LSQUARE", "["),
  ("TT_RSQUARE", "]"),
  ("TT_DOT", "."),
  ("TT_BITAND", "&"),
  ("TT_BITNOT", "~"),
  ("TT_BITOR", "|"),
  ("TT_BITXOR", "^"),
  ("TT_SUB", "-"),
  ("TT_ADD", "+"),
  ("TT_MUL", "*"),
  ("TT_DIV", "/"),
  ("TT_BACKSLASH", "\\"),
  ("TT_BACKTICK", "`"),
  ("TT_MOD", "%"),
  ("TT_LT", "<"),
  ("TT_GT", ">"),
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
print "__TT_REPR__ = [None] * TT_UNKNOWN" 
for name,pattern in TOKENS:
    print "__TT_REPR__[%s] = '%s'" % (name, name)

"""
print "# ************************ LEXER*****************************"
for name,pattern in TOKENS:
    print "    ('%s', %s)," % (pattern, name)
"""

