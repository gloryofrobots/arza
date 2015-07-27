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

obool ointeger_init(OState* S) {
	ointegers(S)->NotFound = OInteger(-1);
	ointegers(S)->Lesser = OInteger(-1);
	ointegers(S)->Greater = OInteger(1);
	ointegers(S)->Equal = OInteger(0);
	return OTRUE;
}

