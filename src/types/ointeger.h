#ifndef OINTEGER_H_
#define OINTEGER_H_

#include <core/obuiltin.h>

static ObinAny obin_integer_new(obin_integer number) {
	ObinAny result;

	result = obin_any_new();
	obin_any_init_integer(result, number);
	return result;
}

ObinAny obin_integer_to_hex_string(ObinState* S, ObinAny self);

#define OINT(number) obin_integer_new(number)

#define obin_is_integer_fit_to_memsize(number) \
	(obin_any_integer(number) > 0 && obin_any_integer(number) < OBIN_MEM_MAX)
/*
	case EOBIN_TYPE_INTEGER:
		_snprintf(temp, _TEMP_BUFFER_SIZE, OBIN_INTEGER_FORMATTER,
				obin_any_integer(any));
		return obin_string_new(state, temp);
		break;
	case EOBIN_TYPE_FLOAT:
		_snprintf(temp, _TEMP_BUFFER_SIZE, OBIN_FLOAT_FORMATTER,
				obin_any_float(any));
		return obin_string_new(state, temp);
		break;
*/
ObinNativeTraits* obin_integer_traits();


#endif /* OINTEGER_H_ */
