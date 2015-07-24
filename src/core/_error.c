#include <obin.h>

obool obin_module_error_init(OState* state) {
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

OAny obin_raise_error(OState* state, OAny exception) {
	return exception;
}

OAny obin_raise(OState* state, OAny trait, ostring message, OAny argument) {
	obin_panic(message);
	return trait;
}

OAny obin_raise_vargs(OState* state, OAny trait, ostring message, ...) {
	va_list myargs;
	va_start(myargs, message);
	obin_log(state, message, myargs);
	va_end(myargs);
	obin_abort();
	return trait;
}
