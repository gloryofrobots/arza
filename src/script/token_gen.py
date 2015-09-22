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
  ("TT_THEN", "then"),
  ("TT_END", "end"),
  ("TT_FUNC", "func"),
  ("TT_CELL", "cell"),
  ("TT_AND", "and"),
  ("TT_OR", "or"),
  ("TT_NOT", "not"),
  ("TT_ELLIPSIS", "..."),
  ("TT_ADD_ASSIGN", "+="),
  ("TT_SUB_ASSIGN", "-="),
  ("TT_MUL_ASSIGN", "*="),
  ("TT_DIV_ASSIGN", "/="),
  ("TT_MOD_ASSIGN", "%="),
  ("TT_AND_ASSIGN", "&="),
  ("TT_XOR_ASSIGN", "^="),
  ("TT_OR_ASSIGN", "|="),

  ("TT_RSHIFT", ">>"),
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
  ("TT_DIVIDE", "/"),
  ("TT_MOD", "%"),
  ("TT_LESS", "<"),
  ("TT_GREATER", ">"),
  ("TT_QUESTION", "?")
  ("TT_UNDEFINED", None)
]

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

