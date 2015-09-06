#include <obin.h>
#include "lex.yy.c"

OBEHAVIOR_DECLARE(__NODE_BEHAVIOR__);

OCELL_DECLARE(_ONode,
	OAny items;
    ochar * raw;
    oint raw_length;
    oint arity;
    OAny value;
    TokenType type;
   	oint line;
   	oint level;
);

#define _node(self) ((_ONode*) OAny_cellVal(self))
#define _node_items(self) (_node(self)->items)

#define _node_setfirst(S, self, value) (osetfirst(S, _node_items(self), value))
#define _node_setsecond(S, self, value) (osetsecond(S, _node_items(self), value))
#define _node_setthird(S, self, value) (osetthird(S, _node_items(self), value))

#define _node_first(S, self) (ofirst(S, _node_items(self)))
#define _node_second(S, self) (osecond(S, _node_items(self)))
#define _node_third(S, self) (othird(S, _node_items(self)))

#define _node_raw(self) (_node(self)->raw)
#define _node_raw_length(self) (_node(self)->raw_length)
#define _node_type(self) (_node(self)->type)
#define _node_line(self) (_node(self)->line)
#define _node_arity(self) (_node(self)->arity)
#define _node_value(self) (_node(self)->value)
#define _node_level(self) (_node(self)->level)

static OAny Node__tostring__(OState* S, OAny self) {
	OAny vec = OVector(S, ObinNil);
	OAny result;

	OVector_push(S, vec,
			OString_pack(S, 2, OString(S, "type: "),
				OString(S, TokenTypeStr(_node_type(self)))
			)
	);

	OVector_push(S, vec,
				OString_pack(S, 2, OString(S, "line: "),
							otostring(S, OInteger(_node_line(self)))
				)
	);

	if(_node_arity(self) > 0) {
		OVector_push(S, vec,
				OString_pack(S, 2, OString(S, "first: "),
						otostring(S, _node_first(S, self))
				)
		);
	}

	if(_node_arity(self) > 1) {
		OVector_push(S, vec,
				OString_pack(S, 2, OString(S, "second: "),
						otostring(S, _node_second(S, self))
				)
		);
	}

	if(_node_arity(self) > 2) {
		OVector_push(S, vec,
				OString_pack(S, 2, OString(S, "third: "),
						otostring(S, _node_third(S, self))
				)
		);
	}

	if(!OAny_isNil(_node_value(self))) {
		OVector_push(S, vec,
				OString_pack(S, 2, OString(S, "value: "),
						otostring(S, _node_value(self))
				)
		);
	}

	result = OString_join(S, OString(S, ", "), vec);
	result = oadd(S, OString(S, "{ "), result);
	result = oadd(S, result, OString(S, " }"));

	return result;
}

OBEHAVIOR_DEFINE(__NODE_BEHAVIOR__,
		"__ASTNode__",
		OBEHAVIOR_MEMORY(0, 0),
		OBEHAVIOR_BASE(Node__tostring__, 0, 0, 0, 0, 0),
		OBEHAVIOR_COLLECTION_NULL,
		OBEHAVIOR_GENERATOR_NULL,
		OBEHAVIOR_NUMBER_NULL
);


typedef ofunc_2 NudFunction;
typedef ofunc_2 StdFunction;
typedef ofunc_3 LedFunction;

typedef struct _NodeHandler {
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
	return handler;
}

NodeHandler* ONode_handler(OState* S, OAny self) {
	return handler(S, _node_type(self));
}

OAny ONode_nud(OState* S, OAny parser, OAny self) {
	NodeHandler* handler = ONode_handler(S, self);
	oassert(handler->nud);
	return handler->nud(S, parser, self);
}

obool ONode_hasNud(OState* S, OAny self) {
	NodeHandler* handler = ONode_handler(S, self);

	return handler->nud != 0;
}

OAny ONode_std(OState* S, OAny parser, OAny self) {
	NodeHandler* handler = ONode_handler(S, self);
	oassert(handler->std);
	return handler->std(S, parser, self);
}

obool ONode_hasStd(OState* S, OAny self) {
	NodeHandler* handler = ONode_handler(S, self);

	return handler->std != 0;
}

obool ONode_rbp(OState* S, OAny self) {
	NodeHandler* handler = ONode_handler(S, self);
	return handler->rbp;
}

oint ONode_lbp(OState* S, OAny self) {
	NodeHandler* handler = ONode_handler(S, self);
	return handler->lbp;
}

OAny ONode_led(OState* S, OAny parser, OAny self, OAny left) {
	NodeHandler* handler = ONode_handler(S, self);
	oassert(handler->led);
	return handler->led(S, parser, self, left);
}

obool ONode_hasLed(OState* S, OAny self) {
	NodeHandler* handler = ONode_handler(S, self);
	return handler->led != 0;
}

OAny ONode_init(OState* S, OAny self, omem_t size) {
	_node_arity(self) = size;
	return self;
}

char *_strdup(const char *str)
{
    int n = strlen(str) + 1;
    char *dup = malloc(n);
    if(dup)
    {
        strcpy(dup, str);
    }
    return dup;
}

OAny ONode(OState* S, TokenType type, ostring raw, oint length, oint line) {
	_ONode* node = obin_new(S, _ONode);
	node->type = type;
	/*TODO del it later*/
	node->raw = _strdup(raw);
	node->raw_length = length;
	node->line = line;
	node->value = OString(S, raw);

	/*TODO Allocate 8 subnodes at start, refactor later*/
	node->items = OArray(S, 8);
	node->arity = 0;

	return OCell_new(-125, (OCell*) node, &__NODE_BEHAVIOR__);
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


OAny parse_error(OState* S, OAny parser, ostring message, OAny argument) {
	return oraise(S, oerrors(S)->ParseError, "message", argument);
}

OAny _checkTokenTypes(OState* S, OAny parser, OAny types) {
	OFOREACH_DEFINE(type);

	if(OAny_isNil(types)) {
		return ObinNil;
	}

	if(OAny_isInt(types)) {
		if(OInt_toTokenType(types) != _parser_token_type(parser)) {
			return parse_error(S, parser, "Expected token ", types);
		}

		return ObinNil;
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
	_parser_node(parser) = ONode(S, _parser_token_type(parser), (ostring)_parser_token(parser).data,
			(oint)_parser_token(parser).length, (oint)_parser_token(parser).line);


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

void pnode(OState* S, ostring message, OAny node) {
	printf("\n %s %s ", message, otocstring(S, node));
}

#define PNODE(node) pnode(S, #node, node)

OAny OSyntax_expression(OState *S, OAny parser, oint rbp) {
	printf("\n******************");
	printf("\nrbp %d", rbp);
	OAny previous = _parser_node(parser);
	OParser_advance(S, parser);
	oint lbp;
	PNODE(previous);
	pnode(S, "current", _parser_node(parser));
	OAny left = ONode_nud(S, parser, previous);

	PNODE(left);

	while(OTRUE) {
		lbp = ONode_lbp(S, _parser_node(parser));
		printf("\nlbp %d", lbp);
		if(rbp >= lbp) {
			break;
		}
		previous = _parser_node(parser);
		OParser_advance(S, parser);
		left = ONode_led(S, parser, previous, left);
	}

	return left;
}

OAny OSyntax_statement(OState* S, OAny parser) {
	OAny node = _parser_node(parser);
	OAny value;

	if(ONode_hasStd(S, node)) {
		OParser_advance(S, parser);
		return ONode_std(S, parser, node);
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
OAny OSyntax_statements__defaultendlist__;
OAny OSyntax_statements(OState* S, OAny parser, OAny endlist) {
	OAny s;
	OAny stmts = OVector(S, ObinNil);
	oint length;

	if(OAny_isNil(endlist)) {
		endlist = OSyntax_statements__defaultendlist__;
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

void NodeHandler_setNud(OState* S, TokenType type, NudFunction nud) {
	NodeHandler* h = handler(S, type);
	h->nud = nud;
}

void NodeHandler_setStd(OState* S, TokenType type, StdFunction std) {
	NodeHandler* h = handler(S, type);
	h->std = std;
}

void NodeHandler_setLed(OState* S, TokenType type, oint lbp, LedFunction led) {
	NodeHandler* h = handler(S, type);
	h->lbp = lbp;
	h->led = led;
}

OAny _itself(OState* S, OAny parser, OAny node) {
	return node;
}

OAny _nud_constant(OState* S, OAny parser, OAny node) {
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

	ONode_init(S, node, 2);
	_node_setfirst(S, node, left);

	while(OAny_isNil(exp)) {
		exp = OSyntax_expression(S, parser, h->lbp);
	}

	_node_setsecond(S, node,  exp);
	return node;
}

void _infix(OState* S, TokenType type, oint lbp, LedFunction led) {
	if(led) {
		NodeHandler_setLed(S, type, lbp, led);
	} else {
		NodeHandler_setLed(S, type, lbp, _led_infix);
	}
}

OAny _led_infixr(OState* S, OAny parser, OAny node, OAny left) {
	NodeHandler* h = ONode_handler(S, node);
	ONode_init(S, node, 2);

	_node_setfirst(S, node, left);
	_node_setsecond(S, node,  OSyntax_expression(S, parser, h->lbp - 1));
	return node;
}

void _infixr(OState* S, TokenType type, oint lbp, LedFunction led) {
	if(led) {
		NodeHandler_setLed(S, type, lbp, led);
	} else {
		NodeHandler_setLed(S, type, lbp, _led_infixr);
	}
}

OAny _led_infixr_assign(OState* S, OAny parser, OAny node, OAny left) {
	ONode_init(S, node, 2);

	switch(_node_type(left)) {
	case TT_DOT:
	case TT_LSQUARE:
	case TT_NAME:
	case TT_COMMA:
		break;
	default:
		return parse_error(S, parser, "Bad lvalue in assignment", left);
	}

	_node_setfirst(S, node, left);
	_node_setsecond(S, node,  OSyntax_expression(S, parser, 9));

	return node;
}

void _assignment(OState* S, TokenType type) {
	_infixr(S, type, 10, _led_infixr_assign);
}

OAny _prefix_nud(OState* S, OAny parser, OAny node) {
	ONode_init(S, node, 1);
	_node_setfirst(S, node, OSyntax_expression(S, parser, 70));
	return node;
}

void _prefix(OState* S, TokenType type) {
	NodeHandler_setNud(S, type, _prefix_nud);
}

void _statement(OState* S, TokenType type, StdFunction std) {
	NodeHandler_setStd(S, type, std);
}

void _literal(OState* S, TokenType type) {
	NodeHandler_setNud(S, type, _itself);
}

OAny _nud_empty(OState* S, OAny parser, OAny node) {
	return ObinNil;
}

OAny OParser_parse(OState* S, OAny parser) {
	OParser_advance(S, parser);

	OAny stmts = OSyntax_statements(S, parser, ObinNil);
	OParser_advanceExpected(S, parser, OInteger(TT_ENDSTREAM));
	return stmts;
}

OAny OParser_fromString(OState* S, OAny str) {
	ostring data = OString_cstr(S, str);
	OParser* parser = obin_new(S, OParser);
	parser->lexer = YYLexer_fromString(data);

	return OCell_new(-124, (OCell*) parser, 0);
}

OAny OParser_parseString(OState* S, OAny str) {
	return OParser_parse(S, OParser_fromString(S, str));
}

OAny OParser_parseCString(OState* S, ostring str) {
	return OParser_parseString(S, OString(S, str));
}

obool oparser_init(OState* S) {
	omemset(handlers, 0, sizeof(NodeHandler) * TT_END_TOKEN_TYPE);
	_infix(S, TT_ADD, 50, 0);
	_infix(S, TT_SUB, 50, 0);
	_infix(S, TT_MUL, 60, 0);
	_infix(S, TT_DIVIDE, 60, 0);
	_literal(S, TT_INT);
	_literal(S, TT_FLOAT);
	_literal(S, TT_CHAR);
	_literal(S, TT_STR);

	_assignment(S, TT_ASSIGN);

	OSyntax_statements__defaultendlist__ = OArray_ofInts(S, 4, TT_RCURLY, TT_ENDSTREAM, TT_END, TT_NEWLINE);
	return OTRUE;
}
