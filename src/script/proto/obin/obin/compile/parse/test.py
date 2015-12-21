__author__ = 'gloryofrobots'
def testprogram():
    data = ""
    with open("program.obn") as f:
        data = f.read()

    return data

def test_lexer():
    txt = testprogram()
    lx = obin.compile.lexer.lexer(txt)
    try:
        for tok in lx.tokens():
            print(tok)
    except obin.compile.lexer.LexerError as e:
        print "Lexer Error at ", e.pos
        print txt[e.pos:]
