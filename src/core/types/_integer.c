#include <obin.h>

OAny OInteger_new(oint number) {
	OAny result;

	result = OAny_new();
	OAny_initInteger(result, number);
	return result;
}

OBehavior* obin_integer_behavior() {
	return NULL;
}

obool OInteger_init(OState* state) {
	ointegers(state)->NotFound = OInteger_new(-1);
	ointegers(state)->Lesser = OInteger_new(-1);
	ointegers(state)->Greater = OInteger_new(1);
	ointegers(state)->Equal = OInteger_new(0);
	return OTRUE;
}

