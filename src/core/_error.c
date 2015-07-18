#include <obin.h>

OBIN_MODULE_DECLARE(ERROR);

obin_bool obin_module_error_init(ObinState* state, ObinInternals* internals) {
	OBIN_MODULE_INIT(ERROR);
	internals->errors.MemoryError = ObinNil;
	internals->errors.IOError = ObinNil;
	internals->errors.InternalError = ObinNil;
	internals->errors.RangeError = ObinNil;
	internals->errors.TypeError = ObinNil;
	internals->errors.ValueError = ObinNil;
	internals->errors.IndexError = ObinNil;
	internals->errors.KeyError = ObinNil;

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
