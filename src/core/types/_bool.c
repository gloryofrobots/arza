#include <obin.h>

ObinAny ObinFalse = OBIN_ANY_STATIC_INIT(EOBIN_TYPE_FALSE);
ObinAny ObinTrue = OBIN_ANY_STATIC_INIT(EOBIN_TYPE_TRUE);
ObinAny ObinNil = OBIN_ANY_STATIC_INIT(EOBIN_TYPE_NIL);
ObinAny ObinNothing = OBIN_ANY_STATIC_INIT(EOBIN_TYPE_NOTHING);

ObinAny obin_bool_new(obin_bool condition){
	if(condition){
		return ObinTrue;
	}

	return ObinFalse;
}

static ObinBehavior __TRUE_BEHAVIOR__ = {0};
static ObinBehavior __FALSE_BEHAVIOR__ = {0};

ObinAny __true_tostring__(ObinState* state, ObinAny self) {
	return obin_strings(state)->True;
}

ObinAny __true_tobool__(ObinState* state, ObinAny self){
	return self;
}

ObinAny __clone__(ObinState* state, ObinAny self) {
	return self;
}

ObinAny __true_compare__(ObinState* state, ObinAny self, ObinAny arg1) {
	ObinAny other = obin_tobool(state, arg1);
	if(OAny_isFalse(other)) {
		return obin_integers(state)->Greater;
	}
	if(OAny_isTrue(other)) {
		return obin_integers(state)->Equal;
	}

	return obin_integers(state)->Lesser;
}

ObinAny __true_hash__(ObinState* state, ObinAny self) {
	return obin_integer_new(1);
}

ObinAny __false_tostring__(ObinState* state, ObinAny self){
	return obin_strings(state)->False;
}

ObinAny __false_tobool__(ObinState* state, ObinAny self) {
	return self;
}

ObinAny __false_compare__(ObinState* state, ObinAny self, ObinAny arg1) {
	ObinAny other = obin_tobool(state, arg1);
	if(OAny_isTrue(other)) {
		return obin_integers(state)->Lesser;
	}
	if(OAny_isFalse(other)) {
		return obin_integers(state)->Equal;
	}

	return obin_integers(state)->Lesser;
}

ObinAny __false_hash__(ObinState* state, ObinAny self) {
	return obin_integer_new(1);
}

obin_bool obin_module_bool_init(ObinState* state) {
	__TRUE_BEHAVIOR__.__name__ = "__True__";
	__TRUE_BEHAVIOR__.__tostring__ = __true_tostring__;
	__TRUE_BEHAVIOR__.__tobool__ = __true_tobool__;
	__TRUE_BEHAVIOR__.__clone__ = __clone__;
	__TRUE_BEHAVIOR__.__compare__ = __true_compare__;
	__TRUE_BEHAVIOR__.__hash__ = __true_hash__;

	obin_behaviors(state)->True = &__TRUE_BEHAVIOR__;

	__FALSE_BEHAVIOR__.__name__ = "__False__";
	__FALSE_BEHAVIOR__.__tostring__ = __false_tostring__;
	__FALSE_BEHAVIOR__.__tobool__ = __false_tobool__;
	__FALSE_BEHAVIOR__.__clone__ = __clone__;
	__FALSE_BEHAVIOR__.__compare__ = __false_compare__;
	__FALSE_BEHAVIOR__.__hash__ = __false_hash__;

	obin_behaviors(state)->True = &__FALSE_BEHAVIOR__;

	return OTRUE;
}

ObinBehavior* obin_false_behavior(){
	return &__FALSE_BEHAVIOR__;
}

ObinBehavior* obin_true_behavior() {
	return &__TRUE_BEHAVIOR__;
}
