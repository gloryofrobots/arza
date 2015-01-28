#ifndef OINTEGER_H_
#define OINTEGER_H_

#include "oany.h"

static ObinAny obin_integer_new(obin_integer number) {
	ObinAny result;

	result = obin_any_new();
	obin_any_init_integer(result, number);
	return result;
}

#define obin_is_integer_fit_to_memsize(number) \
	(obin_any_integer(number) > 0 && obin_any_integer(number) < OBIN_MEM_MAX)

ObinTypeTrait* obin_integer_type_trait();



#endif /* OINTEGER_H_ */
