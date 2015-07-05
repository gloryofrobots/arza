#include <obin.h>

ObinAny obin_integer_new(obin_integer number) {
	ObinAny result;

	result = obin_any_new();
	obin_any_init_integer(result, number);
	return result;
}

ObinAny obin_integer_to_hex_string(ObinState* S, ObinAny self){
	return ObinNil;
}

ObinNativeTraits* obin_integer_traits() {
	return ONULL;
}
