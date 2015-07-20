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

ObinAny _obin_error_new(ObinState* state, ObinAny proto, obin_string message, ObinAny argument) {
	return proto;
}

ObinAny obin_raise_error(ObinState* state, ObinAny exception) {
	return exception;
}

ObinAny obin_raise(ObinState* state, ObinAny trait, obin_string message, ObinAny argument) {
	obin_panic(message);
	return trait;
}

ObinAny obin_raise_vargs(ObinState* state, ObinAny trait, obin_string message, ...) {
	va_list myargs;
	va_start(myargs, message);
	obin_log(state, message, myargs);
	va_end(myargs);
	obin_abort();
	return trait;
}
