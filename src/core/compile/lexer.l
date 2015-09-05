%{
#include <stdio.h>
#include <stdlib.h>

typedef enum {
    TT_ENDSTREAM = 0,
    TT_INT = 1,
    TT_FLOAT = 2,
    TT_STR = 3,
    TT_CHAR = 4,
    TT_NAME = 5,
    TT_NEWLINE = 6,
    TT_BREAK = 7,
    TT_CASE = 8,
    TT_CONTINUE = 9,
    TT_DO = 10,
    TT_ELSE = 11,
    TT_FOR = 12,
    TT_WHILE = 13,
    TT_IF = 14,
    TT_THEN = 15,
    TT_END = 16,
    TT_FUNC = 17,
    TT_CELL = 18,
    TT_AND = 19,
    TT_OR = 20,
    TT_NOT = 21,
    TT_ELLIPSIS = 22,
    TT_ADD_ASSIGN = 23,
    TT_SUB_ASSIGN = 24,
    TT_MUL_ASSIGN = 25,
    TT_DIV_ASSIGN = 26,
    TT_MOD_ASSIGN = 27,
    TT_AND_ASSIGN = 28,
    TT_XOR_ASSIGN = 29,
    TT_OR_ASSIGN = 30,
    TT_RSHIFT = 31,
    TT_LSHIFT = 32,
    TT_ARROW = 33,
    TT_FAT_ARROW = 34,
    TT_EQ = 35,
    TT_LE = 36,
    TT_GE = 37,
    TT_NE = 38,
    TT_SEMI = 39,
    TT_COLON = 40,
    TT_LCURLY = 41,
    TT_RCURLY = 42,
    TT_COMMA = 43,
    TT_ASSIGN = 44,
    TT_LPAREN = 45,
    TT_RPAREN = 46,
    TT_LSQUARE = 47,
    TT_RSQUARE = 48,
    TT_DOT = 49,
    TT_BITAND = 50,
    TT_BITNOT = 51,
    TT_BITOR = 52,
    TT_BITXOR = 53,
    TT_SUB = 54,
    TT_ADD = 55,
    TT_MUL = 56,
    TT_DIVIDE = 57,
    TT_MOD = 58,
    TT_LESS = 59,
    TT_GREATER = 60,
    TT_QUESTION = 61,
    TT_UNKNOWN = 62,
    TT_END_TOKEN_TYPE = 63
} TokenType;

%}
%option reentrant
%option yylineno
%option noyywrap

/* Universal Character Name */
UCN     (\\u[0-9a-fA-F]{4}|\\U[0-9a-fA-F]{8})

O   [0-7]
D   [0-9]
NZ  [1-9]
L   [a-zA-Z_]
A   [a-zA-Z_0-9]
H   [a-fA-F0-9]
HP  (0[xX])
E   ([Ee][+-]?{D}+)
P   ([Pp][+-]?{D}+)
CP  (u|U|L)
SP  (u8|u|U|L)
ES  (\\(['"\?\\abfnrtv]|[0-7]{1,3}|x[a-fA-F0-9]+))
WS  [ \t\v\n\f]

STRING  \"([^"\\]|\\['"?\\abfnrtv]|\\[0-7]{1,3}|\\[Xx][0-9a-fA-F]+|{UCN})*\"
CHAR \'([^'\\]|\\['"?\\abfnrtv]|\\[0-7]{1,3}|\\[Xx][0-9a-fA-F]+|{UCN})+\'
NAME ([_a-zA-Z]|{UCN})([_a-zA-Z0-9]|{UCN})*

%%
^[ ]*\n  {/* Ignore blank lines. */}
\n  { return TT_NEWLINE;  }

 /* constants */
{HP}{H}+       { return TT_INT; }
{NZ}{D}*       { return TT_INT; }
"0"{O}*        { return TT_INT; }
{CP}?"'"([^'\\\n]|{ES})+"'"   { return TT_INT; }

{D}+{E}?        { return TT_FLOAT; }
{D}*"."{D}+{E}?      { return TT_FLOAT; }
{D}+"."{E}?      { return TT_FLOAT; }
{HP}{H}+{P}      { return TT_FLOAT; }
{HP}{H}*"."{H}+{P}     { return TT_FLOAT; }
{HP}{H}+"."{P}     { return TT_FLOAT; }
"break" { return TT_BREAK; }
"case" { return TT_CASE; }
"continue" { return TT_CONTINUE; }
"do" { return TT_DO; }
"else" { return TT_ELSE; }
"for" { return TT_FOR; }
"while" { return TT_WHILE; }
"if" { return TT_IF; }
"then" { return TT_THEN; }
"end" { return TT_END; }
"func" { return TT_FUNC; }
"cell" { return TT_CELL; }
"and" { return TT_AND; }
"or" { return TT_OR; }
"not" { return TT_NOT; }
"..." { return TT_ELLIPSIS; }
"+=" { return TT_ADD_ASSIGN; }
"-=" { return TT_SUB_ASSIGN; }
"*=" { return TT_MUL_ASSIGN; }
"/=" { return TT_DIV_ASSIGN; }
"%=" { return TT_MOD_ASSIGN; }
"&=" { return TT_AND_ASSIGN; }
"^=" { return TT_XOR_ASSIGN; }
"|=" { return TT_OR_ASSIGN; }
">>" { return TT_RSHIFT; }
"<<" { return TT_LSHIFT; }
"->" { return TT_ARROW; }
"=>" { return TT_FAT_ARROW; }
"==" { return TT_EQ; }
"<=" { return TT_LE; }
">=" { return TT_GE; }
"!=" { return TT_NE; }
";" { return TT_SEMI; }
":" { return TT_COLON; }
"{" { return TT_LCURLY; }
"}" { return TT_RCURLY; }
"," { return TT_COMMA; }
"=" { return TT_ASSIGN; }
"(" { return TT_LPAREN; }
")" { return TT_RPAREN; }
"[" { return TT_LSQUARE; }
"]" { return TT_RSQUARE; }
"." { return TT_DOT; }
"&" { return TT_BITAND; }
"~" { return TT_BITNOT; }
"|" { return TT_BITOR; }
"^" { return TT_BITXOR; }
"-" { return TT_SUB; }
"+" { return TT_ADD; }
"*" { return TT_MUL; }
"/" { return TT_DIVIDE; }
"%" { return TT_MOD; }
"<" { return TT_LESS; }
">" { return TT_GREATER; }
"?" { return TT_QUESTION; }

{CHAR} {return TT_CHAR;}
{STRING} {return TT_STR;}

{NAME} {return TT_NAME;}

 /* Ignore comments and whitespace. */
#[^\n]*     {}
{WS}   {}

<<EOF>>     {return TT_ENDSTREAM;}

. { return TT_UNKNOWN; }

%%
 
const char * TokenTypeStr(TokenType type) {
  switch(type) {
   case TT_ENDSTREAM: return "TT_ENDSTREAM";
    case TT_INT: return "TT_INT";
    case TT_FLOAT: return "TT_FLOAT";
    case TT_STR: return "TT_STR";
    case TT_CHAR: return "TT_CHAR";
    case TT_NAME: return "TT_NAME";
    case TT_NEWLINE: return "TT_NEWLINE";
    case TT_BREAK: return "TT_BREAK";
    case TT_CASE: return "TT_CASE";
    case TT_CONTINUE: return "TT_CONTINUE";
    case TT_DO: return "TT_DO";
    case TT_ELSE: return "TT_ELSE";
    case TT_FOR: return "TT_FOR";
    case TT_WHILE: return "TT_WHILE";
    case TT_IF: return "TT_IF";
    case TT_THEN: return "TT_THEN";
    case TT_END: return "TT_END";
    case TT_FUNC: return "TT_FUNC";
    case TT_CELL: return "TT_CELL";
    case TT_AND: return "TT_AND";
    case TT_OR: return "TT_OR";
    case TT_NOT: return "TT_NOT";
    case TT_ELLIPSIS: return "TT_ELLIPSIS";
    case TT_ADD_ASSIGN: return "TT_ADD_ASSIGN";
    case TT_SUB_ASSIGN: return "TT_SUB_ASSIGN";
    case TT_MUL_ASSIGN: return "TT_MUL_ASSIGN";
    case TT_DIV_ASSIGN: return "TT_DIV_ASSIGN";
    case TT_MOD_ASSIGN: return "TT_MOD_ASSIGN";
    case TT_AND_ASSIGN: return "TT_AND_ASSIGN";
    case TT_XOR_ASSIGN: return "TT_XOR_ASSIGN";
    case TT_OR_ASSIGN: return "TT_OR_ASSIGN";
    case TT_RSHIFT: return "TT_RSHIFT";
    case TT_LSHIFT: return "TT_LSHIFT";
    case TT_ARROW: return "TT_ARROW";
    case TT_FAT_ARROW: return "TT_FAT_ARROW";
    case TT_EQ: return "TT_EQ";
    case TT_LE: return "TT_LE";
    case TT_GE: return "TT_GE";
    case TT_NE: return "TT_NE";
    case TT_SEMI: return "TT_SEMI";
    case TT_COLON: return "TT_COLON";
    case TT_LCURLY: return "TT_LCURLY";
    case TT_RCURLY: return "TT_RCURLY";
    case TT_COMMA: return "TT_COMMA";
    case TT_ASSIGN: return "TT_ASSIGN";
    case TT_LPAREN: return "TT_LPAREN";
    case TT_RPAREN: return "TT_RPAREN";
    case TT_LSQUARE: return "TT_LSQUARE";
    case TT_RSQUARE: return "TT_RSQUARE";
    case TT_DOT: return "TT_DOT";
    case TT_BITAND: return "TT_BITAND";
    case TT_BITNOT: return "TT_BITNOT";
    case TT_BITOR: return "TT_BITOR";
    case TT_BITXOR: return "TT_BITXOR";
    case TT_SUB: return "TT_SUB";
    case TT_ADD: return "TT_ADD";
    case TT_MUL: return "TT_MUL";
    case TT_DIVIDE: return "TT_DIVIDE";
    case TT_MOD: return "TT_MOD";
    case TT_LESS: return "TT_LESS";
    case TT_GREATER: return "TT_GREATER";
    case TT_QUESTION: return "TT_QUESTION";
    case TT_UNKNOWN: return "TT_UNKNOWN";
  }
} 

typedef struct {
  yyscan_t scanner;
  YY_BUFFER_STATE buffer;
  struct {
    char * data;
    int length;
    TokenType type;
    int line;
  } token;
} YYLexer;

YYLexer* YYLexer_new() {
  YYLexer* lexer = malloc(sizeof(YYLexer));
  lexer->token.type = TT_UNKNOWN;
  yylex_init(&lexer->scanner);

  return lexer;
}

YYLexer* YYLexer_fromFile(FILE* file) {
  YYLexer* lexer = YYLexer_new();
  lexer->buffer = yy_create_buffer(file, YY_BUF_SIZE, lexer->scanner); 
  yy_switch_to_buffer(lexer->buffer, lexer->scanner); 

  return lexer;
}

YYLexer* YYLexer_fromBytes(char* bytes, size_t length) {
  YYLexer* lexer = YYLexer_new();
  lexer->buffer = yy_scan_bytes(bytes, length, lexer->scanner); 
  yy_switch_to_buffer(lexer->buffer, lexer->scanner); 
  
  return lexer;
}

YYLexer* YYLexer_fromString(const char* string) {
  YYLexer* lexer = YYLexer_new();
  lexer->buffer = yy_scan_string(string, lexer->scanner); 
  yy_switch_to_buffer(lexer->buffer, lexer->scanner); 
  
  return lexer;
}

TokenType YYLexer_next(YYLexer* lexer) {
  lexer->token.type = yylex(lexer->scanner);
  lexer->token.data = yyget_text(lexer->scanner);
  lexer->token.length = yyget_leng(lexer->scanner);
  lexer->token.line = yyget_lineno(lexer->scanner);
  return lexer->token.type;
}

void YYLexer_destroy(YYLexer* lexer) {
  yy_delete_buffer(lexer->buffer, lexer->scanner);
  yylex_destroy(lexer->scanner);
}

int main () {
  FILE* f= fopen("test.c","r");
  YYLexer* lexer = YYLexer_fromFile(f);
  //YYLexer* lexer = YYLexer_fromString("\nx +456 - 5566 for if else\n\n\nb+yyu\n");
  
  while(YYLexer_next(lexer) != TT_ENDSTREAM) {
    printf("%s %s (%d) at %d,\n", TokenTypeStr(lexer->token.type), lexer->token.data, 
    lexer->token.length, lexer->token.line);
  }
  YYLexer_destroy(lexer);
}
