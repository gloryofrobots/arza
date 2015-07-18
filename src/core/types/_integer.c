#include <obin.h>

ObinAny obin_integer_new(obin_integer number) {
	ObinAny result;

	result = obin_any_new();
	obin_any_init_integer(result, number);
	return result;
}

ObinNativeTraits* obin_integer_traits() {
	return NULL;
}

obin_bool obin_module_integer_init(ObinState* state, ObinInternals* internals) {
	internals->integers.NotFound = obin_integer_new(-1);
	internals->integers.Lesser = obin_integer_new(-1);
	internals->integers.Greater = obin_integer_new(1);
	internals->integers.Equal = obin_integer_new(0);
	return OTRUE;
}

