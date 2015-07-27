#include <obin.h>

OBehavior __BEHAVIOR__ = {0};

obool ofloat_init(OState* state) {
	obehaviors(state)->Float = &__BEHAVIOR__;
	return OTRUE;
}

OAny OFloat(ofloat number) {
	OAny result;

	result = OAny_new();
	OAny_initFloat(result, number);
	return result;
}
