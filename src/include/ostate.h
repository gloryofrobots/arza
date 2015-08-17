#ifndef OSTATE_H_
#define OSTATE_H_
#include "oany.h"
typedef struct _OBehavior OBehavior;
/************************* STATE *************************************/
typedef struct _OMemory OMemory;

typedef struct _OInternals {
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
		OAny ZeroDivisionError;
	} errors;

	struct _ObinInternalBehaviors {
		OBehavior* True;
		OBehavior* False;
		OBehavior* Nil;
		OBehavior* Nothing;
		OBehavior* Float;
		OBehavior* Integer;
		OBehavior* Character;
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
#define obehaviors(S) (&S->internals->behaviors)

#endif /* OSTATE_H_ */
