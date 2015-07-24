#include <obin.h>

obin_bool obin_module_error_init(ObinState* state) {
	obin_errors(state)->MemoryError = ObinNil;
	obin_errors(state)->IOError = ObinNil;
	obin_errors(state)->InternalError = ObinNil;
	obin_errors(state)->RangeError = ObinNil;
	obin_errors(state)->TypeError = ObinNil;
	obin_errors(state)->ValueError = ObinNil;
	obin_errors(state)->IndexError = ObinNil;
	obin_errors(state)->KeyError = ObinNil;

	return OTRUE;
}

OAny _obin_error_new(ObinState* state, OAny proto, obin_string message, OAny argument) {
	return proto;
}

OAny obin_raise_error(ObinState* state, OAny exception) {
	return exception;
}

OAny obin_raise(ObinState* state, OAny trait, obin_string message, OAny argument) {
	obin_panic(message);
	return trait;
}

OAny obin_raise_vargs(ObinState* state, OAny trait, obin_string message, ...) {
	va_list myargs;
	va_start(myargs, message);
	obin_log(state, message, myargs);
	va_end(myargs);
	obin_abort();
	return trait;
}
