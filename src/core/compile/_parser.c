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

#define _node_first(self) (_node_items(self)[0])
#define _node_second(self) (_node_items(self)[1])
#define _node_third(self) (_node_items(self)[2])

#define _node_raw(self) (_node(self)->items)
#define _node_raw_length(self) (_node(self)->items)
#define _node_type(self) (_node(self)->items)
#define _node_line(self) (_node(self)->items)
#define _node_arity(self) (_node(self)->arity)
#define _node_value(self) (_node(self)->value)

typedef ofunc_2 NudFunction;
typedef ofunc_2 StdFunction;
typedef ofunc_3 LedFunction;

typedef struct _NodeHandler {
	obool initialized;
	NudFunction nud;
	StdFunction std;
	LedFunction led;
	oint lbp;
	oint rbp;
	OAny value;
} NodeHandler;

NodeHandler handlers [TT_END_TOKEN_TYPE];

NodeHandler* handler(OState* S, TokenType type) {
	oassert(type < TT_END_TOKEN_TYPE);

	NodeHandler* handler = &(handlers[type]);
	oassert(handler->initialized);
	return handler;
}

NodeHandler* ONode_handler(OState* S, OAny self) {
	return handler(S, _node_type(self));
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
	_node_arity(self) = size;
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

	/*TODO Allocate 8 subnodes at start, refactor later*/
	node->items = OArray(S, 8);
	node->arity = 0;

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

	return OParser_advanceExpected(S, parser, OTuple(S, 2, OInteger(TT_SEMI), OInteger(TT_NEWLINE)));
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

OAny OSyntax_statement(OState* S, OAny parser) {
	OAny node = _parser_node(parser);
	OAny value;

	if(ONode_hasStd(S, node)) {
		OParser_advance(S, parser);
		return ONode_std(S, node);
	}

	value = OSyntax_expression(S, parser, 0);
	OSyntax_endOfExpression(S, parser);

	return value;
}

obool OParser_tokenIsOneOf(OState* S, OAny parser, OAny tokenTypes) {
	OFOREACH_DEFINE(type);

	OFOREACH(S, tokenTypes, type,
			if(_parser_token_type(parser) == OInt_toTokenType(type)) {
				return OTRUE;
			}
	);

	return OFALSE;
}

OAny OSyntax_statements(OState* S, OAny parser, OAny endlist) {
	static OAny __defaultendlist__ = OArray_ofInts(S, 4, TT_RCURLY, TT_ENDSTREAM, TT_END, TT_NEWLINE);
	OAny s;
	OAny stmts = OVector(S, ObinNil);
	obool check = OFALSE;
	oint length;

	if(OAny_isNil(endlist)) {
		endlist = __defaultendlist__;
	}

	while(OTRUE) {
		if(OParser_tokenIsOneOf(S, parser, endlist)){
			break;
		}

		s = OSyntax_statement(S, parser);
		if(OAny_isNil(s)) {
			continue;
		}
		OVector_push(S, stmts, s);
	}

	length = OAny_intVal(olength(S, stmts));

	if(length == 0) {
		return ObinNil;
	} else if(length == 1) {
		return ofirst(S, stmts);
	}

	return stmts;
}

void NodeHandler_setNud(OState* s, TokenType type, NudFunction nud) {
	NodeHandler* h = handler(S, type);
	h->nud = nud;
}

void NodeHandler_setStd(OState* s, TokenType type, StdFunction std) {
	NodeHandler* h = handler(S, type);
	h->std = std;
}

void NodeHandler_setLed(OState* s, TokenType type, oint lbp, LedFunction led) {
	NodeHandler* h = handler(S, type);
	h->lbp = lbp;
	h->led = led;
}

OAny _nud_constant(OState* S, OAny node) {
	NodeHandler* h = ONode_handler(S, node);
	_node_value(node) = h->value;
	ONode_init(S, node, 0);
	return node;
}

void _constant(OState* S, TokenType type, OAny value) {
	NodeHandler* h = handler(S, type);
	h->value = value;
	NodeHandler_setNud(S, type, _nud_constant);
}

OAny _led_infix(OState* S, OAny parser, OAny node, OAny left) {
	OAny exp = ObinNil;
	NodeHandler* h = ONode_handler(S, node);

	ONode_init(node, 2);
	_node_first(node) = left;

	while(OAny_isNil(exp)) {
		exp = OSyntax_expression(S, parser, h->lbp);
	}

	_node_second(node) = exp;

	return node;
}

void _infix(OState* S, TokenType type, oint lbp, LedFunction led) {
	NodeHandler_setLed(S, type, lbp, led || _led_infix);
}

OAny _led_infixr(OState* S, OAny parser, OAny node, OAny left) {
	OAny exp = ObinNil;
	NodeHandler* h = ONode_handler(S, node);
	ONode_init(node, 2);

	_node_first(node) = left;
	_node_second(node) = OSyntax_expression(S, parser, h->lbp - 1);

	return node;
}

void _infixr(OState* S, TokenType type, oint lbp, LedFunction led) {
	NodeHandler_setLed(S, type, lbp, led || _led_infixr);
}

OAny _led_infixr_assign(OState* S, OAny parser, OAny node, OAny left) {
	OAny exp = ObinNil;
	NodeHandler* h = ONode_handler(S, node);
	ONode_init(node, 2);

	switch(_node_type(left)) {
	case TT_DOT:
	case TT_LSQUARE:
	case TT_NAME:
	case TT_COMMA:
		break;
	default:
		return parse_error(S, parser, "Bad lvalue in assignment", left);
	}

	_node_first(node) = left;
	_node_second(node) = OSyntax_expression(S, parser, 9);

	return node;
}

void _assignment(OState* S, TokenType type) {
	_infixr(S, type, 10, _led_infixr_assign);
}

OAny _prefix_nud(OState* S, OAny parser, OAny node) {
	OAny exp = ObinNil;
	NodeHandler* h = ONode_handler(S, node);
	ONode_init(node, 1);
	_node_first(node) = OSyntax_expression(S, parser, 70);

	return node;
}

void _prefix(OState* S, TokenType type) {
	NodeHandler_setNud(S, type, _prefix_nud);
}

void _statement(OState* S, TokenType type, StdFunction std) {
	NodeHandler_setStd(S, type, std);
}

OAny _nud_empty(OState* S, OAny parser, OAny node) {
	return ObinNil;
}

OParser_parse(OState* S, OAny parser) {
	OAny stmts = OSyntax_statements(S, parser, ObinNil);
	OParser_advanceExpected(S, parser, OInteger(TT_ENDSTREAM));
	return stmts;
}

obool oparser_init(OState* S) {
	omemset(handlers, 0, sizeof(NodeHandler) * TT_END_TOKEN_TYPE);
	_infix(S, TT_ADD, 50, 0);
	_infix(S, TT_SUB, 50, 0);
	_infix(S, TT_MUL, 60, 0);
	_infix(S, TT_DIVIDE, 60, 0);

	_assignment(S, TT_ASSIGN);

	return OTRUE;
}
