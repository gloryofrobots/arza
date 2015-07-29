#include <obin.h>
/*TODO rename it*/
OAny ObinFalse = OBIN_ANY_STATIC_INIT(EOBIN_TYPE_FALSE);
OAny ObinTrue = OBIN_ANY_STATIC_INIT(EOBIN_TYPE_TRUE);
OAny ObinNil = OBIN_ANY_STATIC_INIT(EOBIN_TYPE_NIL);
OAny ObinNothing = OBIN_ANY_STATIC_INIT(EOBIN_TYPE_NOTHING);

OAny OBool(obool condition){
	if(condition){
		return ObinTrue;
	}

	return ObinFalse;
}

static OBehavior __TRUE_BEHAVIOR__ = {0};
static OBehavior __FALSE_BEHAVIOR__ = {0};

OAny __true_tostring__(OState* S, OAny self) {
	return ostrings(S)->True;
}

OAny __true_tobool__(OState* S, OAny self){
	return self;
}

OAny __clone__(OState* S, OAny self) {
	return self;
}

OAny __true_compare__(OState* S, OAny self, OAny arg1) {
	OAny other = otobool(S, arg1);
	if(OAny_isFalse(other)) {
		return ointegers(S)->Greater;
	}
	if(OAny_isTrue(other)) {
		return ointegers(S)->Equal;
	}

	return ointegers(S)->Lesser;
}

OAny __true_hash__(OState* S, OAny self) {
	return OInteger(1);
}

OAny __false_tostring__(OState* S, OAny self){
	return ostrings(S)->False;
}

OAny __false_tobool__(OState* S, OAny self) {
	return self;
}

OAny __false_compare__(OState* S, OAny self, OAny arg1) {
	OAny other = otobool(S, arg1);
	if(OAny_isTrue(other)) {
		return ointegers(S)->Lesser;
	}
	if(OAny_isFalse(other)) {
		return ointegers(S)->Equal;
	}

	return ointegers(S)->Lesser;
}

OAny __false_hash__(OState* S, OAny self) {
	return OInteger(1);
}

obool obool_init(OState* S) {
	__TRUE_BEHAVIOR__.__name__ = "__True__";
	__TRUE_BEHAVIOR__.__tostring__ = __true_tostring__;
	__TRUE_BEHAVIOR__.__tobool__ = __true_tobool__;
	__TRUE_BEHAVIOR__.__clone__ = __clone__;
	__TRUE_BEHAVIOR__.__compare__ = __true_compare__;
	__TRUE_BEHAVIOR__.__hash__ = __true_hash__;

	obehaviors(S)->True = &__TRUE_BEHAVIOR__;

	__FALSE_BEHAVIOR__.__name__ = "__False__";
	__FALSE_BEHAVIOR__.__tostring__ = __false_tostring__;
	__FALSE_BEHAVIOR__.__tobool__ = __false_tobool__;
	__FALSE_BEHAVIOR__.__clone__ = __clone__;
	__FALSE_BEHAVIOR__.__compare__ = __false_compare__;
	__FALSE_BEHAVIOR__.__hash__ = __false_hash__;

	obehaviors(S)->True = &__FALSE_BEHAVIOR__;

	return OTRUE;
}

OBehavior* obin_false_behavior(){
	return &__FALSE_BEHAVIOR__;
}

OBehavior* obin_true_behavior() {
	return &__TRUE_BEHAVIOR__;
}
