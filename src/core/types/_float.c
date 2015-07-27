#include <obin.h>
#define __TypeName__ "__Float__"

#define _CHECK_SELF_TYPE(S, self, method) \
	if(!OAny_isFloat(self)) { \
		return oraise(S, oerrors(S)->TypeError, \
				__TypeName__"."#method "call from other type", self); \
	}

#define _CHECK_INT_ARG_TYPE(S, self, method) \
	if(!OAny_isAny(self)) { \
		return oraise(S, oerrors(S)->TypeError, \
				__TypeName__"."#method " argument is not __Integer", self); \
	}

#define _CHECK_ARG_TYPE(S, self, method) \
	if(!OAny_isFloat(self)) { \
		return oraise(S, oerrors(S)->TypeError, \
				__TypeName__"."#method " argument is not "__TypeName__, self); \
	}

#define _float(any) OAny_toFloat(any)

OAny OFloat(ofloat number) {
	OAny result;

	result = OAny_new();
	OAny_initFloat(result, number);
	return result;
}

OAny OFloat_fromInt(OAny i) {
	return OFloat((ofloat) OAny_toInt(i));
}

static OAny __tostring__(OState* S, OAny self) {
	oint size;

	ochar buffer[OBIN_FLOAT_REPR_SIZE] = {'\0'};

	_CHECK_SELF_TYPE(S, self, __tostring__);
	size = osprintf(buffer, OBIN_FLOAT_FORMATTER, _float(self));
	if(size < 0) {
        return oraise(S, oerrors(S)->TypeError,
                __TypeName__ "__tostring__ error in inernal function osprintf", self);
	}

	printf("\nFloat__tostring__ %s\n", buffer);
	return OString(S, buffer);
}

static OAny __tobool__(OState* S, OAny self) {
	_CHECK_SELF_TYPE(S, self, __tobool__);
	return OBool(_float(self) != 0);
}

static OAny __clone__(OState* S, OAny self) {
	_CHECK_SELF_TYPE(S, self, __clone__);
	return self;
}

static OAny __compare__(OState* S, OAny self, OAny arg1) {
	int result;
	_CHECK_SELF_TYPE(S, self, __compare__);
	_CHECK_ARG_TYPE(S, arg1, __compare__);

	if(_float(self) == _float(arg1)) {
		result = 0;
	} else if(_float(self) > _float(arg1)) {
		result = 1;
	} else {
		result = -1;
	}

	return OFloat(result);
}

static OAny __hash__(OState* S, OAny self) {
	_CHECK_SELF_TYPE(S, self, __hash__);
	return OInteger((oint)_float(self));
}

static OAny __tointeger__(OState* S, OAny self) {
	_CHECK_SELF_TYPE(S, self, __tointeger__);
	return OInteger((oint)_float(self));
}

static OAny __tofloat__(OState* S, OAny self) {
	_CHECK_SELF_TYPE(S, self, __tofloat__);
	return self;
}

static OAny __tonegative__(OState* S, OAny self) {
	_CHECK_SELF_TYPE(S, self, __tonegative__);
	return OFloat(-1* _float(self));
}

static OAny __add__(OState* S, OAny self, OAny arg1) {
	_CHECK_SELF_TYPE(S, self, __add__);
	_CHECK_ARG_TYPE(S, arg1, __add__);
	return OFloat(_float(self) + _float(arg1));
}

static OAny __subtract__(OState* S, OAny self, OAny arg1) {
	_CHECK_SELF_TYPE(S, self, __subtract__);
	_CHECK_ARG_TYPE(S, arg1, __subtract__);
	return OFloat(_float(self) - _float(arg1));
}

static OAny __divide__(OState* S, OAny self, OAny arg1) {
	_CHECK_SELF_TYPE(S, self, __divide__);
	_CHECK_ARG_TYPE(S, arg1, __divide__);
	return OFloat(_float(self) / _float(arg1));
}

static OAny __multiply__(OState* S, OAny self, OAny arg1) {
	_CHECK_SELF_TYPE(S, self, __multiply__);
	_CHECK_ARG_TYPE(S, arg1, __multiply__);
	return OFloat(_float(self) * _float(arg1));
}

static OAny __mod__(OState* S, OAny self, OAny arg1) {
	_CHECK_SELF_TYPE(S, self, __mod__);
	_CHECK_SELF_TYPE(S, arg1, __mod__);
	return OFloat(fmod(_float(self), _float(arg1)));
}

OBehavior __BEHAVIOR__ = {0};

obool ofloat_init(OState* S) {
	__BEHAVIOR__.__tostring__ = __tostring__;
	__BEHAVIOR__.__tobool__ = __tobool__;
	__BEHAVIOR__.__clone__ = __clone__;
	__BEHAVIOR__.__hash__ = __hash__;
	__BEHAVIOR__.__compare__ = __compare__;
	__BEHAVIOR__.__tointeger__ = __tointeger__;
	__BEHAVIOR__.__tofloat__ = __tofloat__;
	__BEHAVIOR__.__tonegative__ = __tonegative__;
	__BEHAVIOR__.__add__ = __add__;
	__BEHAVIOR__.__subtract__ = __subtract__;
	__BEHAVIOR__.__divide__ = __divide__;
	__BEHAVIOR__.__multiply__ = __multiply__;
	__BEHAVIOR__.__mod__ = __mod__;

	obehaviors(S)->Float = &__BEHAVIOR__;
	return OTRUE;
}

