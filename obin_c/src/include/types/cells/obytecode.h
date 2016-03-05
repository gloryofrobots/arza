#ifndef OBYTECODE_H_
#define OBYTECODE_H_
#include "obuiltin.h"
/*TOS = top of the stack*/
typedef enum  {
	/*PUSH_OBJECT(name_literal_id) LOOKUP FOR name with name_literal_id and push object*/
    PUSH_OBJECT,

	/*PUSH_CONSTANT(type) PUSH constant types such as True,False. use high bits for constant type*/
    PUSH_CONSTANT,

	/*PUSH_LITERAL(literal_id) push literal from executable*/
    PUSH_LITERAL,

	/*PUSH_VECTOR(size) */
    PUSH_VECTOR,

    /*PUSH_BLOCK(block_id) push block from executable*/
	PUSH_BLOCK,

	/*ASSIGN(varname_literal_id) create variable with name of literal(varname_literal_id) and value of TOS */
    ASSIGN,
    /*LOOKUP(name_literal_id) lookup name in TOS*/
	LOOKUP,
	/*CALL(count_arguments)  call executable with list of arguments  where
	 *  executable will be at stack[-count_arguments]*/
	CALL,

	/*POP_TOP(0)*/
    POP_TOP,
	/*RETURN(0) return top of the stack*/
    RETURN,

    BLOCK_RETURN,
} EOBYTECODE;

OAny OBytecode(OState* S, omem_t capacity);
OAny OBytecode_pack(OState* S, oint count, ...);
OAny OBytecode_append(OState* S, OAny self, EOBYTECODE low, obytecode high);
EOBYTECODE OBytecode_getCommand(OState* S, OAny self, oint index);
obytecode OBytecode_getArgument(OState* S, OAny self, oint index);
OAny OBytecode_set(OState* S, OAny self, oindex_t index, EOBYTECODE high, obytecode low);

#endif /* OBYTECODE_H_ */
