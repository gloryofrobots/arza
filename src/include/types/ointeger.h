#ifndef OINTEGER_H_
#define OINTEGER_H_

#include "obuiltin.h"

obool obin_module_integer_init(OState* state);


OAny obin_integer_new(oint number);

#define obin_is_integer_fit_to_memsize(number) \
	(obin_any_integer(number) > 0 && obin_any_integer(number) < OBIN_MEM_MAX)

#endif /* OINTEGER_H_ */
