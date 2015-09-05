#include <obin.h>
#include "lex.yy.c"
OCELL_DECLARE(OParser,
	YYLexer * lexer;
);
#define _parser(self) ((OParser*) OAny_cellVal(self))
#define _parser_lexer(self) (_parser(self)->lexer)
#define _parser_token(parser)  (_parser_lexer(parser)->token)
#define _parser_token_type(parser) (_parser_token(parser).type)

OAny OParser_fromString(OState* S, OAny str) {
	ostring data = OString_cstr(S, str);
	OParser* parser = obin_new(S, OParser);
	parser->lexer = YYLexer_fromString(data);

	return OCell_new(-124, (OCell*) parser, 0);
}

typedef struct _NodeHandler {
	obool initialized;
	ofunc_1 nud;
	ofunc_1 std;
	ofunc_2 led;
	oint lbp;
} NodeHander;

NodeHander handlers [TT_END_TOKEN_TYPE];

obool oparser_init(OState* S) {
	omemset(handlers, 0, sizeof(NodeHander) * TT_END_TOKEN_TYPE);
	return OTRUE;
}

OCELL_DECLARE(_ONode,
	OAny items;
    ochar * raw;
    oint raw_length;
    oint arity;
    OAny value;
    TokenType type;
   	oint line;
);

#define _node(self) ((_ONode*) OAny_cellVal(self))
#define _node_items(self) (_node(self)->items)
#define _node_raw(self) (_node(self)->items)
#define _node_raw_length(self) (_node(self)->items)
#define _node_type(self) (_node(self)->items)
#define _node_line(self) (_node(self)->items)
#define _node_arity(self) (_node(self)->arity)
#define _node_value(self) (_node(self)->value)

OAny ONode_init(OState* S, OAny self, omem_t size) {
	_node_items(self) = OArray(S, size);
	return self;
}

OAny ONode(OState* S, TokenType type, ostring raw, oint length, oint line) {
	_ONode* node = obin_new(S, _ONode);
	node->type = type;
	/*TODO del it later*/
	node->raw = strdup(raw);
	node->raw_length = length;
	node->line = line;
	node->value = OString(S, raw);
	return OCell_new(-125, (_ONode) node, 0);
}

#define OInt_toTokenType(t) ((TokenType) OAny_intVal(t))

OAny parse_error(OState* S, OAny parser, ostring message, OAny argument) {
	return oraise(S, oerrors(S)->ParseError, "message", argument);
}

OAny _checkTokenTypes(OState* S, OAny parser, OAny types) {
	OFOREACH_DEFINE(type);

	if(OAny_isNil(types)) {
		return ObinNil;
	}

	if(!OAny_isTuple(types)) {
		if(OInt_toTokenType(types) != _parser_token_type(parser)) {
			return parse_error(S, parser, "Expected token ", types);
		}
	}

	OFOREACH(S, types, type,
		if(_parser_token_type(parser) == OInt_toTokenType(type)) {
			return ObinNil;
	});

	return parse_error(S, parser, "Expected one of the tokens ", types);
}


OAny OParser_advance(OState* S, OAny self, OAny expected) {
	OAny node;
	_checkTokenTypes(S, self, expected);
	if(_parser_token_type(self) == TT_ENDSTREAM) {
		return ObinNil;
	}

	YYLexer_next(_parser_lexer(self));
	node = ONode(S, _parser_token_type(self), (ostring)_parser_token(self)->data,
			(oint)_parser_token(self)->length, (oint)_parser_token(self)->line);


	return node;
}

