#include <obin.h>

ObinAny obin_float_new(obin_float number) {
	ObinAny result;

	result = obin_any_new();
	obin_any_init_float(result, number);
	return result;
}

ObinNativeTraits* obin_float_traits() {
	return ONULL;
}
