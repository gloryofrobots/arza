#ifndef OFLOAT_H_
#define OFLOAT_H_
#include <core/obuiltin.h>

ObinAny obin_float_new(obin_float number) {
	ObinAny result;

	result = obin_any_new();
	obin_any_init_float(result, number);
	return result;
}

ObinNativeTraits* obin_float_traits();


#endif
