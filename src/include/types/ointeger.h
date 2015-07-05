#ifndef OINTEGER_H_
#define OINTEGER_H_

#include "obuiltin.h"

ObinAny obin_integer_new(obin_integer number);


#define obin_is_integer_fit_to_memsize(number) \
	(obin_any_integer(number) > 0 && obin_any_integer(number) < OBIN_MEM_MAX)

ObinAny obin_integer_to_hex_string(ObinState* S, ObinAny self);
ObinNativeTraits* obin_integer_traits();

#endif /* OINTEGER_H_ */
