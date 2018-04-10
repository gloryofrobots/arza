TOKENS = [
  ("TT_ENDSTREAM", None,),
  ("TT_INT", None,),
  ("TT_FLOAT", None,),
  ("TT_STR", None,),
  ("TT_MULTI_STR", None,),
  ("TT_CHAR", None,),
  ("TT_NAME", None),
  ("TT_OPERATOR", None),
  ("TT_VOID", None),
  ("TT_NIL", None),
  ("TT_TRUE", "true"),
  ("TT_FALSE", "false"),
  ("TT_SELF", None),

  ("TT_FUN", "fun"),

  ("TT_RECEIVE", "case"),
  ("TT_MATCH", "case"),
  ("TT_CASE", "case"),

  ("TT_WHILE", "while"),
  ("TT_FOR", "for"),
  ("TT_BREAK", "break"),
  ("TT_CONTINUE", "continue"),

  ("TT_CLASS", "class"),
  ("TT_EXTENDS", "extends"),

  ("TT_IF", "if"),
  ("TT_ELIF", "elif"),
  ("TT_ELSE", "else"),
  ("TT_THEN", "then"),
  ("TT_WHEN", "when"),

  ("TT_TRY", "try"),
  ("TT_THROW", "throw"),
  ("TT_CATCH", "catch"),
  ("TT_FINALLY", "finally"),

  ("TT_LET", "let"),

  ("TT_OF", "of"),
  ("TT_IN", "in"),
  ("TT_IS", "is"),
  ("TT_AS", "as"),

  ("TT_NOT", "not"),
  ("TT_AND", "and"),
  ("TT_OR", "or"),

  ("TT_IMPORT", "import"),
  ("TT_INCLUDE", "include"),
  ("TT_FROM", "from"),
  ("TT_HIDING", "hiding"),
  ("TT_USE", "use"),

  ("TT_END_EXPR", ";"),
  ("TT_NEWLINE", "(newline)"),

  ("TT_INFIXL", "infixl"),
  ("TT_INFIXR", "infixr"),
  ("TT_PREFIX", "prefix"),

  ("TT_WILDCARD", "_"),
  ("TT_GOTO", "goto"),
  ("TT_ARROW", "->"),
  ("TT_AT_SIGN", "@"),
  ("TT_DOUBLE_AT", "@@"),
  ("TT_DOLLAR", "$"),


  ("TT_SHARP", "#"),

  ("TT_JUXTAPOSITION", " "),
  ("TT_LCURLY", "{"),
  ("TT_RCURLY", "}"),
  ("TT_COMMA", ","),
  ("TT_ASSIGN", "="),

  ("TT_INFIX_DOT_LCURLY", ".{"),
  ("TT_LPAREN", "("),
  ("TT_RPAREN", ")"),

  ("TT_LSQUARE", "["),
  ("TT_RSQUARE", "]"),
  ("TT_COLON", ":"),
  ("TT_DOUBLE_COLON", "::"),
  ("TT_DOT", "."),
  ("TT_TRIPLE_DOT", "..."),
  ("TT_DOUBLE_DOT", ".."),
  ("TT_BACKTICK_NAME", "`"),
  ("TT_BACKTICK_OPERATOR", "`"),

  ("TT_LT", "<"),
  ("TT_GT", ">"),
  ("TT_GE", ">="),
  ("TT_LE", "<="),
  ("TT_EQ", "=="),
  ("TT_NE", "!="),

  ("TT_BOR", "|"),
  ("TT_BNOT", "~"),
  ("TT_BAND", "&"),
  ("TT_BXOR", "^"),
  ("TT_BRSH", ">>"),
  ("TT_BLSH", "<<"),

  ("TT_ADD", "+"),
  ("TT_SUB", "+"),
  ("TT_MUL", "*"),
  ("TT_DIV", "/"),
  ("TT_POW", "**"),
  ("TT_NEG", "-"),

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
print "def token_type_to_u(ttype):"
print "    return __TT_REPR__[ttype]"
print
print "def token_type_to_s(ttype):"
print "    return str(__TT_REPR__[ttype])"


# print "# ************************ COMPILE SWITCH*****************************"
# for number, token in enumerate(TOKENS):
#     t_str = token[0].replace("TT_", "")
#     print "    elif %s == t:" % token[0]
#     print "        self._compile_%s(code, node)" % t_str

