%{
#include <stdio.h>
#include <stdlib.h>

typedef enum {
  TT_END=0,
  TT_INT,
  TT_FLOAT,
  TT_STR,
  TT_CHAR,
  TT_NAME,
  TT_NEWLINE,

  
  TT_PUNCT,  
} TokenType;

%}
%option reentrant
%option yylineno
%option noyywrap
/* some complex named patterns */

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
FS  (f|F|l|L)
CP  (u|U|L)
SP  (u8|u|U|L)
ES  (\\(['"\?\\abfnrtv]|[0-7]{1,3}|x[a-fA-F0-9]+))
WS  [ \t\v\n\f]

STRING  \"([^"\\]|\\['"?\\abfnrtv]|\\[0-7]{1,3}|\\[Xx][0-9a-fA-F]+|{UCN})*\"
CHAR \'([^'\\]|\\['"?\\abfnrtv]|\\[0-7]{1,3}|\\[Xx][0-9a-fA-F]+|{UCN})+\'
%%
 /* constants */

{HP}{H}+       { return TT_INT; }
{NZ}{D}*       { return TT_INT; }
"0"{O}*        { return TT_INT; }
{CP}?"'"([^'\\\n]|{ES})+"'"   { return TT_INT; }

{D}+{E}{FS}?        { return TT_FLOAT; }
{D}*"."{D}+{E}?{FS}?      { return TT_FLOAT; }
{D}+"."{E}?{FS}?      { return TT_FLOAT; }
{HP}{H}+{P}{FS}?      { return TT_FLOAT; }
{HP}{H}*"."{H}+{P}{FS}?     { return TT_FLOAT; }
{HP}{H}+"."{P}{FS}?     { return TT_FLOAT; }

{CHAR} {return TT_CHAR;}
{STRING} {return TT_STR;}

^[ ]*\n  {/* Ignore blank lines. */}
\n  { return TT_NEWLINE;  }

[A-Za-z_][A-Za-z_0-9]*      {return TT_NAME;}

[~!@#$%^&*()_+{}|:;<>,./?=-\\]+     {return TT_PUNCT;}

 /* Ignore comments and whitespace. */
#[^\n]*     {}
{WS}   {}

<<EOF>>     {return TT_END;}

%%
 
const char * TokenTypeStr(TokenType type) {
  switch(type) {
    case TT_END:
      return "TT_END";
    case TT_INT:
      return "TT_INT";
    case TT_FLOAT:
      return "TT_FLOAT";
    case TT_STR:
      return "TT_STR";
    case TT_NAME:
      return "TT_NAME";
    case TT_NEWLINE:
      return "TT_NEWLINE";
    case TT_PUNCT:
      return "TT_PUNCT";
  }
}

typedef struct {
    const char * data;
    int length;
    TokenType type;
    int line;
} Token;

Token make_token(TokenType type, const char* data, int line) {
  Token token;
  token.type = type;
  token.data = strdup(data);
  token.line = line;
}


int main () {
 yyscan_t scanner;
 int tok_type;

 yylex_init(&scanner);

 while ((tok_type=yylex(scanner)) != TT_END) {
    printf("%s <%s>,\n", TokenTypeStr(tok_type), yyget_text(scanner));
 }
    
 yylex_destroy(scanner);
 return 0;
}
