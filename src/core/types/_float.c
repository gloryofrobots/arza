#include <obin.h>

OBehavior __BEHAVIOR__ = {0};

obool obin_module_float_init(OState* state) {
	obehaviors(state)->Float = &__BEHAVIOR__;
	return OTRUE;
}

OAny obin_float_new(ofloat number) {
	OAny result;

	result = OAny_new();
	OAny_initFloat(result, number);
	return result;
}
