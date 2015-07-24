#include <obin.h>

ObinBehavior __BEHAVIOR__ = {0};

obin_bool obin_module_float_init(ObinState* state) {
	obin_behaviors(state)->Float = &__BEHAVIOR__;
	return OTRUE;
}

OAny obin_float_new(obin_float number) {
	OAny result;

	result = OAny_new();
	OAny_initFloat(result, number);
	return result;
}
