#include <obin.h>

obool OError_Init(OState* state) {
	oerrors(state)->MemoryError = ObinNil;
	oerrors(state)->IOError = ObinNil;
	oerrors(state)->InternalError = ObinNil;
	oerrors(state)->RangeError = ObinNil;
	oerrors(state)->TypeError = ObinNil;
	oerrors(state)->ValueError = ObinNil;
	oerrors(state)->IndexError = ObinNil;
	oerrors(state)->KeyError = ObinNil;

	return OTRUE;
}

OAny _obin_error_new(OState* state, OAny proto, ostring message, OAny argument) {
	return proto;
}

OAny OError_raise(OState* state, OAny exception) {
	return exception;
}

OAny oraise(OState* state, OAny trait, ostring message, OAny argument) {
	opanic(message);
	return trait;
}

OAny oraise_vargs(OState* state, OAny trait, ostring message, ...) {
	va_list myargs;
	va_start(myargs, message);
	olog(state, message, myargs);
	va_end(myargs);
	oabort();
	return trait;
}
