#include <obin.h>

OAny obin_integer_new(oint number) {
	OAny result;

	result = OAny_new();
	OAny_initInteger(result, number);
	return result;
}

OBehavior* obin_integer_behavior() {
	return NULL;
}

obool obin_module_integer_init(OState* state) {
	ointegers(state)->NotFound = obin_integer_new(-1);
	ointegers(state)->Lesser = obin_integer_new(-1);
	ointegers(state)->Greater = obin_integer_new(1);
	ointegers(state)->Equal = obin_integer_new(0);
	return OTRUE;
}

