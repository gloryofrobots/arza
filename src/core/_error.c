#include <obin.h>

obool oerror_init(OState* S) {
	oerrors(S)->MemoryError = ObinNil;
	oerrors(S)->IOError = ObinNil;
	oerrors(S)->InternalError = ObinNil;
	oerrors(S)->RangeError = ObinNil;
	oerrors(S)->TypeError = ObinNil;
	oerrors(S)->ValueError = ObinNil;
	oerrors(S)->IndexError = ObinNil;
	oerrors(S)->KeyError = ObinNil;

	return OTRUE;
}

OAny _obin_error_new(OState* S, OAny proto, ostring message, OAny argument) {
	return proto;
}

OAny OError_raise(OState* S, OAny exception) {
	return exception;
}

OAny oraise(OState* S, OAny trait, ostring message, OAny argument) {
	opanic(message);
	return trait;
}

OAny oraise_vargs(OState* S, OAny trait, ostring message, ...) {
	va_list myargs;
	va_start(myargs, message);
	olog(S, message, myargs);
	va_end(myargs);
	oabort();
	return trait;
}
