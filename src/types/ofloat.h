#ifndef OFLOAT_H_
#define OFLOAT_H_
#include "oany.h"

ObinAny obin_float_new(obin_float number) {
	ObinAny result;

	result = obin_any_new();
	obin_any_init_float(result, number);
	return result;
}

ObinTypeTrait* obin_float_type_trait();


#endif
