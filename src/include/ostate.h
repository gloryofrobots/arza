#ifndef OSTATE_H_
#define OSTATE_H_
#include "oany.h"
typedef struct _OBehavior OBehavior;
/************************* STATE *************************************/
typedef struct _OMemory OMemory;

typedef struct _OInternals {
	struct _ObinInternalCells {
		OAny __Cell__;
		OAny __String__;
		OAny __Array__;
		OAny __Table__;
		OAny __ProtoCell__;
		OAny __Tuple__;
		OAny __List__;
		OAny __Stream__;
	} cells;

	struct _ObinInternalIntegers {
		OAny NotFound;
		OAny Lesser;
		OAny Greater;
		OAny Equal;
	} integers;

	struct _ObinInternalStrings{
		OAny Nil;
		OAny True;
		OAny False;
		OAny Nothing;
		OAny PrintSeparator;
		OAny Empty;
		OAny Space;
		OAny TabSpaces;
	} strings;

	struct _ObinInternalErrors{
		OAny Error;
		OAny MemoryError;
		OAny IOError;
		OAny InternalError;
		OAny RangeError;
		OAny TypeError;
		OAny ValueError;
		OAny IndexError;
		OAny KeyError;
	} errors;

	struct _ObinInternalBehaviors {
		OBehavior* True;
		OBehavior* False;
		OBehavior* Nil;
		OBehavior* Nothing;
		OBehavior* Float;
		OBehavior* Integer;
		OBehavior* Char;
	} behaviors;

} OInternals;


typedef struct _ObinState {
	OAny globals;
	OMemory* memory;
	OInternals* internals;
} OState;

#define oerrors(S) (&S->internals->errors)
#define ointegers(S) (&S->internals->integers)
#define ostrings(S) (&S->internals->strings)
#define ocells(S) (&S->internals->cells)
#define obehaviors(S) (&S->internals->behaviors)

#endif /* OSTATE_H_ */
