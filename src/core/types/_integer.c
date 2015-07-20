#include <obin.h>

ObinAny obin_integer_new(obin_integer number) {
	ObinAny result;

	result = obin_any_new();
	obin_any_init_integer(result, number);
	return result;
}

ObinBehavior* obin_integer_behavior() {
	return NULL;
}

obin_bool obin_module_integer_init(ObinState* state) {
	obin_integers(state) = obin_integer_new(-1);
	obin_integers(state) = obin_integer_new(-1);
	obin_integers(state) = obin_integer_new(1);
	obin_integers(state) = obin_integer_new(0);
	return OTRUE;
}

