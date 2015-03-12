#ifndef OERROR_H_
#define OERROR_H_

#include "oany.h"

ObinAny obin_error_new(ObinState* state, ObinAny proto, ObinAny message,
		ObinAny args);
ObinAny obin_raise(ObinState* state, ObinAny exception);

#define _OBIN_RAISE(state, proto, message, argtuple) \
		obin_raise(state, obin_error_new(state, proto, obin_string_new(state, message), argtuple))

#define _OBIN_RAISE_1(state, proto, message, argument) \
		_OBIN_RAISE(state, proto, message, obin_tuple_build(state, 1, argument))

#define _OBIN_RAISE_2(state, proto, message, arg1, arg2) \
		_OBIN_RAISE(state, proto, message, obin_tuple_build(state, 2, arg1, arg2))

#define _OBIN_RAISE_3(state, proto, message, arg1, arg2, arg3) \
		_OBIN_RAISE(state, proto, message, obin_tuple_build(state, 3, arg1, arg2, arg3))

/* constructors */
/* TODO add __func__ to error and maybe do something like const strings */
#define obin_raise_internal(state) \
		obin_raise(state, ObinInternalError)

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



#endif /* OERROR_H_ */
