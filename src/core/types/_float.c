#include <obin.h>

ObinBehavior __BEHAVIOR__ = {0};

obin_bool obin_module_float_init(ObinState* state) {
	obin_behaviors(state)->Float = &__BEHAVIOR__;
	return OTRUE;
}

ObinAny obin_float_new(obin_float number) {
	ObinAny result;

	result = obin_any_new();
	obin_any_init_float(result, number);
	return result;
}
