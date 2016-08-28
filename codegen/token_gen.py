TOKENS = [
  ("TT_ENDSTREAM", None,),
  ("TT_INT", None,),
  ("TT_FLOAT", None,),
  ("TT_STR", None,),
  ("TT_MULTI_STR", None,),
  ("TT_CHAR", None,),
  ("TT_NAME", None),
  ("TT_TICKNAME", None),
  ("TT_OPERATOR", None),
  ("TT_FUN", "fun"),
  ("TT_MATCH", "match"),
  ("TT_WITH", "with"),
  ("TT_CASE", "|"),

  ("TT_EXTEND", "extend"),
  ("TT_TYPE", "type"),

  ("TT_IF", "if"),
  ("TT_ELIF", "elif"),
  ("TT_ELSE", "else"),

  ("TT_THEN", "then"),
  ("TT_WHEN", "when"),

  ("TT_OF", "of"),
  ("TT_DEF", "def"),
  ("TT_LET", "let"),
  ("TT_IN", "in"),
  ("TT_AS", "as"),
  ("TT_AND", "and"),
  ("TT_OR", "or"),
  ("TT_NOT", "not"),
  ("TT_TRUE", "true"),
  ("TT_FALSE", "false"),
  ("TT_TRY", "try"),
  ("TT_THROW", "throw"),
  ("TT_CATCH", "catch"),
  ("TT_FINALLY", "finally"),
  ("TT_MODULE", "module"),
  ("TT_IMPORT", "import"),
  ("TT_FROM", "from"),
  ("TT_HIDING", "hiding"),
  ("TT_HIDE", "hide"),
  ("TT_EXPORT", "export"),
  ("TT_TRAIT", "trait"),
  ("TT_USE", "use"),
  ("TT_GENERIC", "generic"),
  ("TT_INTERFACE", "interface"),
  ("TT_END_EXPR", ";"),
  ("TT_NEWLINE", "(newline)"),
  ("TT_ELLIPSIS", "..."),
  ("TT_WILDCARD", "_"),
  ("TT_GOTO", "goto"),
  ("TT_ARROW", "->"),
  ("TT_FAT_ARROW", "=>"),
  ("TT_AT_SIGN", "@"),
  ("TT_SHARP", "#"),
  ("TT_JUXTAPOSITION", " "),
  ("TT_LCURLY", "{"),
  ("TT_RCURLY", "}"),
  ("TT_COMMA", ","),
  ("TT_ASSIGN", "="),

  ("TT_INFIX_DOT_LCURLY", ".{"),
  ("TT_INFIX_DOT_LSQUARE", ".["),
  ("TT_LPAREN", "("),
  ("TT_RPAREN", ")"),
  ("TT_PREFIX", "prefix"),
  ("TT_INFIXL", "infixl"),
  ("TT_INFIXR", "infixr"),

  ("TT_LSQUARE", "["),
  ("TT_RSQUARE", "]"),
  ("TT_DOT", "."),
  ("TT_COLON", ":"),
  ("TT_DOUBLE_COLON", "::"),
  ("TT_BACKTICK_NAME", "`"),
  ("TT_BACKTICK_OPERATOR", "`"),
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
print "# ************************ LALAN TOKENS*****************************"
for number, token in enumerate(TOKENS):
    print "%s = %d" % (token[0],number)


print "# ************************ LALAN TOKENS REPR *****************************"
S = "__TT_REPR__ = ["
for name,pattern in TOKENS:
    S += "%s, " % str(("u\"%s\"" % name))
S += "]"
print S
print """
def token_type_to_u(ttype):
    return __TT_REPR__[ttype]


def token_type_to_s(ttype):
    return str(__TT_REPR__[ttype])
"""

# print "# ************************ COMPILE SWITCH*****************************"
# for number, token in enumerate(TOKENS):
#     t_str = token[0].replace("TT_", "")
#     print "    elif %s == t:" % token[0]
#     print "        self._compile_%s(code, node)" % t_str

