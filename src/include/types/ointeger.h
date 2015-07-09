#ifndef OINTEGER_H_
#define OINTEGER_H_

#include "obuiltin.h"

typedef struct _ObinIntegers {
	ObinAny NotFound;
    ObinAny Lesser;
    ObinAny Greater;
    ObinAny Equal;
} ObinIntegers;

obin_bool obin_module_integer_init(ObinState* state);

ObinIntegers* obin_integers();

ObinAny obin_integer_new(obin_integer number);

#define obin_is_integer_fit_to_memsize(number) \
	(obin_any_integer(number) > 0 && obin_any_integer(number) < OBIN_MEM_MAX)

ObinNativeTraits* obin_integer_traits();

#endif /* OINTEGER_H_ */
