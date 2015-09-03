echo "------------lex lexer.l"
lex lexer.l
echo "----------------------------gcc lex.yy.c -o lexer -ll"
gcc lex.yy.c -o lexer -ll
cat test.c | ./lexer

