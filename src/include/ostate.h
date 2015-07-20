#ifndef OSTATE_H_
#define OSTATE_H_
#include "oany.h"

/************************* STATE *************************************/
typedef struct _ObinMemory ObinMemory;

typedef struct _ObinInternals {
	struct _ObinInternalCells {
		ObinAny __Cell__;
		ObinAny __String__;
		ObinAny __Array__;
		ObinAny __Table__;
		ObinAny __ProtoCell__;
		ObinAny __Tuple__;
		ObinAny __List__;
		ObinAny __Stream__;
	} cells;

	struct _ObinInternalIntegers {
		ObinAny NotFound;
		ObinAny Lesser;
		ObinAny Greater;
		ObinAny Equal;
	} integers;

	struct _ObinInternalStrings{
		ObinAny Nil;
		ObinAny True;
		ObinAny False;
		ObinAny Nothing;
		ObinAny PrintSeparator;
		ObinAny Empty;
		ObinAny Space;
		ObinAny TabSpaces;
	} strings;

	struct _ObinInternalErrors{
		ObinAny Error;
		ObinAny MemoryError;
		ObinAny IOError;
		ObinAny InternalError;
		ObinAny RangeError;
		ObinAny TypeError;
		ObinAny ValueError;
		ObinAny IndexError;
		ObinAny KeyError;
	} errors;
} ObinInternals;


typedef struct _ObinState {
	ObinAny globals;
	ObinMemory* memory;
	ObinInternals* internals;
} ObinState;


#define obin_errors(state) (&state->internals->errors)
#define obin_integers(state) (&state->internals->integers)
#define obin_strings(state) (&state->internals->strings)
#define obin_cells(state) (&state->internals->cells)

#endif /* OSTATE_H_ */
