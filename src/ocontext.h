#ifndef OBIN_OCONTEXT_H_
#define OBIN_OCONTEXT_H_
#include <ointernal.h>

typedef struct {
	ObinAny Nil;
	ObinAny True;
	ObinAny False;
	ObinAny Nothing;
	ObinAny PrintSeparator;
} ObinInternalStrings;

typedef struct {
	ObinInternalStrings internal_strings;
} ObinContext;

ObinContext* obin_ctx_get();
#endif /* OCONTEXT_H_ */
