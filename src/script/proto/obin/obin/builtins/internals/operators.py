OP_IS = u"___is"
OP_NE = u"___ne"
OP_EQ = u"___eq"
OP_NOT = u"___not"
OP_ISNOT = u"___isnot"
OP_IN = u"___in"
OP_ADD = u"___add"
OP_MOD = u"___mod"
OP_MUL = u"___mul"
OP_DIV = u"___div"
OP_SUB = u"___sub"
OP_UMINUS = u"___uminus"
OP_UPLUS = u"___uplus"
OP_GE = u"___ge"
OP_GT = u"___gt"
OP_LT = u"___lt"
OP_LE = u"___le"
OP_BITNOT = u"___bitnot"
OP_BITOR = u"___bitor"
OP_BITXOR = u"___bitxor"
OP_BITAND = u"___bitand"
OP_LSH = u"___lsh"
OP_RSH = u"___rsh"
OP_URSH = u"___ursh"
OP_CONS = u"___cons"
OP_NOTIN = u"___notin"
OP_NOTA = u"___nota"
OP_ISA = u"___isa"
OP_KINDOF = u"___kindof"

# """
# precedence 35
# |
# """
# """
# precedence 40
# ^
# """
# """
# precedence 45
# &
# """
# """
# precedence 50
# in, is, <, <=, >, >=, !=, == isnot, notin, isa, nota
# """
# """
# precedence 55
# >> << >>>
# """
# """
# precedence 60
# + -
# """
# """
# precedence 65
# * / %
# """
# infixr(parser, TT_BITOR, 35)
#
# infixr(parser, TT_BITXOR, 40)
#
# infixr(parser, TT_BITAND, 45)
# infixr(parser, TT_DOUBLE_COLON, 70)
#
#
# infix(parser, TT_LT, 50, led_infix)
# infix(parser, TT_LE, 50, led_infix)
# infix(parser, TT_GT, 50, led_infix)
# infix(parser, TT_GE, 50, led_infix)
# infix(parser, TT_NE, 50, led_infix)
# infix(parser, TT_EQ, 50, led_infix)
#
# infix(parser, TT_LSHIFT, 55, led_infix)
# infix(parser, TT_RSHIFT, 55, led_infix)
# infix(parser, TT_URSHIFT, 55, led_infix)
#
# infix(parser, TT_ADD, 60, led_infix)
# infix(parser, TT_SUB, 60, led_infix)
#
# infix(parser, TT_MUL, 65, led_infix)
# infix(parser, TT_DIV, 65, led_infix)
# infix(parser, TT_MOD, 65, led_infix)
#
#
#
# prefix(parser, TT_BITNOT, prefix_nud)
# prefix(parser, TT_SUB, prefix_unary_minus)
# prefix(parser, TT_ADD, prefix_unary_plus)

