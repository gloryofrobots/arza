#include <obin.h>

OAny OInteger(oint number) {
	OAny result;

	result = OAny_new();
	OAny_initInteger(result, number);
	return result;
}

OBehavior* obin_integer_behavior() {
	return NULL;
}

obool ointeger_init(OState* state) {
	ointegers(state)->NotFound = OInteger(-1);
	ointegers(state)->Lesser = OInteger(-1);
	ointegers(state)->Greater = OInteger(1);
	ointegers(state)->Equal = OInteger(0);
	return OTRUE;
}

