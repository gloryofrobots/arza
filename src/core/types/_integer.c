#include <obin.h>

ObinAny obin_integer_new(obin_integer number) {
	ObinAny result;

	result = obin_any_new();
	obin_any_init_integer(result, number);
	return result;
}

ObinNativeTraits* obin_integer_traits() {
	return NULL;
}

static ObinIntegers _Integers = {
		 {EOBIN_TYPE_INTEGER, {-1}},
		 {EOBIN_TYPE_INTEGER, {-1}},
		 {EOBIN_TYPE_INTEGER, {1}},
		 {EOBIN_TYPE_INTEGER, {0}},
};

obin_bool obin_module_integer_init(ObinState* state) {
/*	_Integers.NotFound = obin_integer_new(-1);
	_Integers.Lesser = obin_integer_new(-1);
	_Integers.Greater = obin_integer_new(1);
	_Integers.Equal = obin_integer_new(0);*/
	return OTRUE;
}

ObinIntegers* obin_integers() {
	return &_Integers;
}
