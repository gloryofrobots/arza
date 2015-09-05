#include <obin.h>
#include "lex.yy.c"

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

typedef struct _NodeHandler {
	obool initialized;
	ofunc_1 nud;
	ofunc_1 std;
	ofunc_2 led;
	oint lbp;
	oint rbp;
} NodeHandler;

NodeHandler handlers [TT_END_TOKEN_TYPE];

NodeHandler* ONode_handler(OState* S, OAny self) {
	oassert(_node_type(self) < TT_END_TOKEN_TYPE);

	NodeHandler* handler = &(handlers[_node_type(self)]);
	oassert(handler->initialized);
	return handler;
}

OAny ONode_nud(OState* S, OAny self) {
	NodeHandler* handler = ONode_handler(S, self);
	oassert(handler->nud);
	return handler->nud(S, self);
}

obool ONode_hasNud(OState* S, OAny self) {
	NodeHandler* handler = ONode_handler(S, self);

	return handler->nud != 0;
}

OAny ONode_std(OState* S, OAny self) {
	NodeHandler* handler = ONode_handler(S, self);
	oassert(handler->std);
	return handler->std(S, self);
}

obool ONode_hasStd(OState* S, OAny self) {
	NodeHandler* handler = ONode_handler(S, self);

	return handler->std != 0;
}

obool ONode_rbp(OState* S, OAny self) {
	NodeHandler* handler = ONode_handler(S, self);
	return handler->rbp;
}

obool ONode_lbp(OState* S, OAny self) {
	NodeHandler* handler = ONode_handler(S, self);
	return handler->lbp;
}

obool ONode_lbp(OState* S, OAny self) {
	NodeHandler* handler = ONode_handler(S, self);

	return handler->rbp;
}

OAny ONode_led(OState* S, OAny self, OAny left) {
	NodeHandler* handler = ONode_handler(S, self);
	oassert(handler->led);
	return handler->led(S, self, left);
}

obool ONode_hasLed(OState* S, OAny self) {
	NodeHandler* handler = ONode_handler(S, self);
	return handler->led != 0;
}

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

OCELL_DECLARE(OParser,
	YYLexer * lexer;
	OAny node;
);

#define _parser(self) ((OParser*) OAny_cellVal(self))
#define _parser_lexer(self) (_parser(self)->lexer)
#define _parser_node(self) (_parser(self)->node)
#define _parser_token(parser)  (_parser_lexer(parser)->token)
#define _parser_token_type(parser) (_parser_token(parser).type)

OAny OParser_fromString(OState* S, OAny str) {
	ostring data = OString_cstr(S, str);
	OParser* parser = obin_new(S, OParser);
	parser->lexer = YYLexer_fromString(data);

	return OCell_new(-124, (OCell*) parser, 0);
}

obool oparser_init(OState* S) {
	omemset(handlers, 0, sizeof(NodeHandler) * TT_END_TOKEN_TYPE);
	return OTRUE;
}

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

OAny OParser_advance(OState* S, OAny parser) {

	if(_parser_token_type(parser) == TT_ENDSTREAM) {
		return ObinNil;
	}

	YYLexer_next(_parser_lexer(parser));
	_parser_node(parser) = ONode(S, _parser_token_type(parser), (ostring)_parser_token(parser)->data,
			(oint)_parser_token(parser)->length, (oint)_parser_token(parser)->line);


	return _parser_node(parser);
}

OAny OParser_advanceExpected(OState* S, OAny parser, OAny expected) {
	_checkTokenTypes(S, parser, expected);
	return OParser_advance(S, parser);
}

OAny OSyntax_endOfExpression(OState *S, OAny parser) {
	if(_parser_token_type(parser) == TT_ENDSTREAM) {
		return ObinNil;
	}

	return OParser_advanceExpected(S, parser, OTuple(S, 2, OInt(TT_SEMI), OInt(TT_NEWLINE)));
}

OAny OSyntax_expression(OState *S, OAny parser, oint rbp) {
	OAny previous = _parser_node(parser);
	OAny current = OParser_advance(S, parser);
	OAny left = ONode_nud(S, previous);
	while(OTRUE) {
		if(rbp >= ONode_rbp(S, current)) {
			break;
		}
		previous = current;
		OParser_advance(S, parser);
		left = ONode_led(S, previous, left);
	}

	return left;
}

