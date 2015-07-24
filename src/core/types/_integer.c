#include <obin.h>

OAny obin_integer_new(obin_integer number) {
	OAny result;

	result = OAny_new();
	OAny_initInteger(result, number);
	return result;
}

OBehavior* obin_integer_behavior() {
	return NULL;
}

obin_bool obin_module_integer_init(ObinState* state) {
	obin_integers(state)->NotFound = obin_integer_new(-1);
	obin_integers(state)->Lesser = obin_integer_new(-1);
	obin_integers(state)->Greater = obin_integer_new(1);
	obin_integers(state)->Equal = obin_integer_new(0);
	return OTRUE;
}

