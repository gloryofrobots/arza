#include <obin.h>

OBIN_MODULE_DECLARE(ERROR);

static ObinInternalErrors _Errors;

ObinInternalErrors* obin_errors() {
	return &_Errors;
}

obin_bool obin_module_error_init(ObinState* state) {
	OBIN_MODULE_INIT(ERROR);
	_Errors.MemoryError = ObinNil;
	_Errors.IOError = ObinNil;
	_Errors.InternalError = ObinNil;
	_Errors.RangeError = ObinNil;
	_Errors.TypeError = ObinNil;
	_Errors.ValueError = ObinNil;
	_Errors.IndexError = ObinNil;
	_Errors.KeyError = ObinNil;

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
