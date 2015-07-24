#include <obin.h>

OAny ObinFalse = OBIN_ANY_STATIC_INIT(EOBIN_TYPE_FALSE);
OAny ObinTrue = OBIN_ANY_STATIC_INIT(EOBIN_TYPE_TRUE);
OAny ObinNil = OBIN_ANY_STATIC_INIT(EOBIN_TYPE_NIL);
OAny ObinNothing = OBIN_ANY_STATIC_INIT(EOBIN_TYPE_NOTHING);

OAny obin_bool_new(obin_bool condition){
	if(condition){
		return ObinTrue;
	}

	return ObinFalse;
}

static OBehavior __TRUE_BEHAVIOR__ = {0};
static OBehavior __FALSE_BEHAVIOR__ = {0};

OAny __true_tostring__(OState* state, OAny self) {
	return ostrings(state)->True;
}

OAny __true_tobool__(OState* state, OAny self){
	return self;
}

OAny __clone__(OState* state, OAny self) {
	return self;
}

OAny __true_compare__(OState* state, OAny self, OAny arg1) {
	OAny other = obin_tobool(state, arg1);
	if(OAny_isFalse(other)) {
		return ointegers(state)->Greater;
	}
	if(OAny_isTrue(other)) {
		return ointegers(state)->Equal;
	}

	return ointegers(state)->Lesser;
}

OAny __true_hash__(OState* state, OAny self) {
	return obin_integer_new(1);
}

OAny __false_tostring__(OState* state, OAny self){
	return ostrings(state)->False;
}

OAny __false_tobool__(OState* state, OAny self) {
	return self;
}

OAny __false_compare__(OState* state, OAny self, OAny arg1) {
	OAny other = obin_tobool(state, arg1);
	if(OAny_isTrue(other)) {
		return ointegers(state)->Lesser;
	}
	if(OAny_isFalse(other)) {
		return ointegers(state)->Equal;
	}

	return ointegers(state)->Lesser;
}

OAny __false_hash__(OState* state, OAny self) {
	return obin_integer_new(1);
}

obin_bool obin_module_bool_init(OState* state) {
	__TRUE_BEHAVIOR__.__name__ = "__True__";
	__TRUE_BEHAVIOR__.__tostring__ = __true_tostring__;
	__TRUE_BEHAVIOR__.__tobool__ = __true_tobool__;
	__TRUE_BEHAVIOR__.__clone__ = __clone__;
	__TRUE_BEHAVIOR__.__compare__ = __true_compare__;
	__TRUE_BEHAVIOR__.__hash__ = __true_hash__;

	obehaviors(state)->True = &__TRUE_BEHAVIOR__;

	__FALSE_BEHAVIOR__.__name__ = "__False__";
	__FALSE_BEHAVIOR__.__tostring__ = __false_tostring__;
	__FALSE_BEHAVIOR__.__tobool__ = __false_tobool__;
	__FALSE_BEHAVIOR__.__clone__ = __clone__;
	__FALSE_BEHAVIOR__.__compare__ = __false_compare__;
	__FALSE_BEHAVIOR__.__hash__ = __false_hash__;

	obehaviors(state)->True = &__FALSE_BEHAVIOR__;

	return OTRUE;
}

OBehavior* obin_false_behavior(){
	return &__FALSE_BEHAVIOR__;
}

OBehavior* obin_true_behavior() {
	return &__TRUE_BEHAVIOR__;
}
