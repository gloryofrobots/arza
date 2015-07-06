#ifndef OERROR_H_
#define OERROR_H_

#include "obuiltin.h"

static ObinAny ObinMemoryError;
static ObinAny ObinIOError;
static ObinAny ObinInternalError;
static ObinAny ObinInvalidSliceError;
static ObinAny ObinTypeError;
static ObinAny ObinValueError;
static ObinAny ObinIndexError;
static ObinAny ObinKeyError;

ObinAny obin_module_error_init(ObinState* state);

ObinAny obin_error_new(ObinState* state, ObinAny proto, obin_string message,
		ObinAny argument);

ObinAny obin_raise(ObinState* state, ObinAny exception);

#define _OBIN_RAISE(state, proto, message, arguments) \
		obin_raise(state, obin_error_new(state, proto, message, arguments))

#define _OBIN_RAISE_1(state, proto, message, argument) \
		_OBIN_RAISE(state, proto, message, obin_tuple_pack(state, 1, argument))

#define _OBIN_RAISE_2(state, proto, message, arg1, arg2) \
		_OBIN_RAISE(state, proto, message, obin_tuple_pack(state, 2, arg1, arg2))

#define _OBIN_RAISE_3(state, proto, message, arg1, arg2, arg3) \
		_OBIN_RAISE(state, proto, message, obin_tuple_pack(state, 3, arg1, arg2, arg3))

/* constructors */
/* TODO add __func__ to error and maybe do something like const strings */
#define obin_raise_internal(state, message, obj) \
		_OBIN_RAISE_1(state, ObinInternalError, message, obj)

#define obin_raise_io_error(state, message, obj) \
		_OBIN_RAISE_1(state, ObinIOError, message, obj)

#define obin_raise_value_error(state, message, obj) \
		_OBIN_RAISE_1(state, ObinValueError, message, obj)

#define obin_raise_type_error(state, message, obj) \
		_OBIN_RAISE_1(state, ObinTypeError, message, obj)

#define obin_raise_memory_error(state, message, obj) \
		_OBIN_RAISE_1(state, ObinTypeError, message, obj)

#define obin_raise_index_error(state, message, obj) \
		_OBIN_RAISE_1(state, ObinIndexError, message, obj)

#define obin_raise_invalid_slice(state, message, start, end) \
		_OBIN_RAISE_2(state, ObinInvalidSliceError, message, start, end)

#define obin_raise_key_error(state, message, obj) \
		_OBIN_RAISE_1(state, ObinKeyError, message, obj)


#endif /* OERROR_H_ */
