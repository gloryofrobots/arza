#include <obin.h>
#define __TypeName__ "__Integer__"

#define _CHECK_SELF_TYPE(S, self, method) \
	if(!OAny_isInt(self)) { \
		return oraise(S, oerrors(S)->TypeError, \
				__TypeName__"."#method "call from other type", self); \
	}

#define _CHECK_ARG_TYPE(S, self, method) \
	if(!OAny_isInt(self)) { \
		return oraise(S, oerrors(S)->TypeError, \
				__TypeName__"."#method " argument is not "__TypeName__, self); \
	}


#define _int(any) OAny_toInt(any)

OAny OInteger(oint number) {
	OAny result;

	result = OAny_new();
	OAny_initInteger(result, number);
	return result;
}

OAny OInteger_fromFloat(OAny f) {
	return OInteger((oint)OAny_toFloat(f));
}

OAny OInteger_fromCFloat(ofloat f) {
	return OInteger((oint)f);
}

static OAny __tostring__(OState* S, OAny self) {
	oint size;

	ochar buffer[OBIN_INTEGER_REPR_SIZE] = {'\0'};

	_CHECK_SELF_TYPE(S, self, __tostring__);
	size = osprintf(buffer, OBIN_INTEGER_FORMATTER, _int(self));
	if(size < 0) {
        return oraise(S, oerrors(S)->TypeError,
                __TypeName__ "__tostring__ error in inernal function osprintf", self);
	}

	return OString(S, buffer);
}

static OAny __tobool__(OState* S, OAny self) {
	_CHECK_SELF_TYPE(S, self, __tobool__);
	return OBool(_int(self) != 0);
}

static OAny __clone__(OState* S, OAny self) {
	_CHECK_SELF_TYPE(S, self, __clone__);
	return self;
}

static OAny __compare__(OState* S, OAny self, OAny arg1) {
	int result;
	_CHECK_SELF_TYPE(S, self, __compare__);
	_CHECK_ARG_TYPE(S, arg1, __compare__);

	if(_int(self) == _int(arg1)) {
		result = 0;
	} else if(_int(self) > _int(arg1)) {
		result = 1;
	} else {
		result = -1;
	}

	return OInteger(result);
}

static OAny __hash__(OState* S, OAny self) {
	_CHECK_SELF_TYPE(S, self, __hash__);
	return self;
}

static OAny __tointeger__(OState* S, OAny self) {
	_CHECK_SELF_TYPE(S, self, __tointeger__);
	return self;
}

static OAny __tofloat__(OState* S, OAny self) {
	_CHECK_SELF_TYPE(S, self, __tofloat__);
	return OFloat((ofloat) _int(self));
}

static obool _isOverflowOnNegate(oint a) {
	if(a == OINT_MIN) {
		return OTRUE;
	}
	return OFALSE;
}

static OAny __tonegative__(OState* S, OAny self) {
	_CHECK_SELF_TYPE(S, self, __tonegative__);
	if(_isOverflowOnNegate(_int(self))) {
		return onumber_from_float(-1* _int(self));
	}

	return OInteger(-1* _int(self));
}

static OAny __invert__(OState* S, OAny self) {
	_CHECK_SELF_TYPE(S, self, __invert__);
	return OInteger(~(_int(self)));
}

static obool _isOverflowOnAdd(oint left, oint right) {
	 if (right > 0 ? left > OINT_MAX - right
	               : left < OINT_MIN - right) {
		 return OTRUE;
	 }

	 return OFALSE;
}

static OAny __add__(OState* S, OAny self, OAny arg1) {
	_CHECK_SELF_TYPE(S, self, __add__);
	_CHECK_ARG_TYPE(S, arg1, __add__);
	if(_isOverflowOnAdd(_int(self), _int(arg1))) {
			return oadd(S, onumber_cast_upper(S, self), onumber_cast_upper(S, arg1));
	}

	return OInteger(_int(self) + _int(arg1));
}

static obool _isOverflowOnSubstract(int left, int right) {
       if (right > 0 ? left < OINT_MIN + right
               : left > OINT_MAX + right) {
           return OTRUE;
       }
       return OFALSE;
}

static OAny __subtract__(OState* S, OAny self, OAny arg1) {
	_CHECK_SELF_TYPE(S, self, __subtract__);
	_CHECK_ARG_TYPE(S, arg1, __subtract__);
	if(_isOverflowOnSubstract(_int(self), _int(arg1))) {
		return osubtract(S, onumber_cast_upper(S, self), onumber_cast_upper(S, arg1));
	}

	return OInteger(_int(self) - _int(arg1));
}

static obool _isOverflowOnDivide(int left, int right) {
	if ((left == OINT_MIN) && (right == -1)) {
       return OTRUE;
	}

	return OFALSE;
}

static OAny __divide__(OState* S, OAny self, OAny arg1) {
	_CHECK_SELF_TYPE(S, self, __divide__);
	_CHECK_ARG_TYPE(S, arg1, __divide__);
	if(_int(arg1) == 0) {
		return oraise(S, oerrors(S)->ZeroDivisionError,
			                __TypeName__ "__divide__  divizion by zero", self);
	}

	if(_isOverflowOnDivide(_int(self), _int(arg1))) {
		return odivide(S, onumber_cast_upper(S, self), onumber_cast_upper(S, arg1));
	}

	if(_int(self) % _int(arg1) != 0) {
		return odivide(S, OFloat_fromInt(self), OFloat_fromInt(arg1));
	}

	return OInteger(_int(self) / _int(arg1));
}

static obool _isOverflowOnMultiply(int left, int right) {
   if (right > 0 ? left > OINT_MAX / right
		   || left < OINT_MIN / right
		   : (right < -1 ? left > OINT_MIN / right
				   || left < OINT_MAX / right : right == -1
				   && left == OINT_MIN)) {
	   return OTRUE;
   }

   return OFALSE;
}

static OAny __multiply__(OState* S, OAny self, OAny arg1) {
	_CHECK_SELF_TYPE(S, self, __multiply__);
	_CHECK_ARG_TYPE(S, arg1, __multiply__);
	if(_isOverflowOnMultiply(_int(self), _int(arg1))) {
		return odivide(S, onumber_cast_upper(S, self), onumber_cast_upper(S, arg1));
	}

	return OInteger(_int(self) * _int(arg1));
}

static OAny __leftshift__(OState* S, OAny self, OAny arg1) {
	_CHECK_SELF_TYPE(S, self, __leftshift__);
	_CHECK_ARG_TYPE(S, arg1, __leftshift__);
	return OInteger(_int(self) << _int(arg1));
}

static OAny __rightshift__(OState* S, OAny self, OAny arg1){
	_CHECK_SELF_TYPE(S, self, __rightshift__);
	_CHECK_ARG_TYPE(S, arg1, __rightshift__);
	return OInteger(_int(self) >> _int(arg1));
}

static OAny __mod__(OState* S, OAny self, OAny arg1) {
	_CHECK_SELF_TYPE(S, self, __mod__);
	_CHECK_ARG_TYPE(S, arg1, __mod__);
	return OInteger(_int(self) % _int(arg1));
}

static OAny __and__(OState* S, OAny self, OAny arg1) {
	_CHECK_SELF_TYPE(S, self, __and__);
	_CHECK_ARG_TYPE(S, arg1, __and__);
	return OInteger(_int(self) & _int(arg1));
}

static OAny __or__(OState* S, OAny self, OAny arg1){
	_CHECK_SELF_TYPE(S, self, __and__);
	_CHECK_ARG_TYPE(S, arg1, __and__);
	return OInteger(_int(self) | _int(arg1));
}

static OAny __xor__(OState* S, OAny self, OAny arg1) {
	_CHECK_SELF_TYPE(S, self, __and__);
	_CHECK_ARG_TYPE(S, arg1, __and__);
	return OInteger(_int(self) ^ _int(arg1));
}

static OBehavior __BEHAVIOR__ = {0};

obool ointeger_init(OState* S) {
	ointegers(S)->NotFound = OInteger(-1);
	ointegers(S)->Lesser = OInteger(-1);
	ointegers(S)->Greater = OInteger(1);
	ointegers(S)->Equal = OInteger(0);

	__BEHAVIOR__.__tostring__ = __tostring__;
	__BEHAVIOR__.__tobool__ = __tobool__;
	__BEHAVIOR__.__clone__ = __clone__;
	__BEHAVIOR__.__hash__ = __hash__;
	__BEHAVIOR__.__compare__ = __compare__;
	__BEHAVIOR__.__tointeger__ = __tointeger__;
	__BEHAVIOR__.__tofloat__ = __tofloat__;
	__BEHAVIOR__.__tonegative__ = __tonegative__;
	__BEHAVIOR__.__invert__ = __invert__;
	__BEHAVIOR__.__add__ = __add__;
	__BEHAVIOR__.__subtract__ = __subtract__;
	__BEHAVIOR__.__divide__ = __divide__;
	__BEHAVIOR__.__multiply__ = __multiply__;
	__BEHAVIOR__.__leftshift__ = __leftshift__;
	__BEHAVIOR__.__rightshift__ = __rightshift__;
	__BEHAVIOR__.__mod__ = __mod__;
	__BEHAVIOR__.__bitand__ = __and__;
	__BEHAVIOR__.__bitor__ = __or__;
	__BEHAVIOR__.__bitxor__ = __xor__;

	obehaviors(S)->Integer = &__BEHAVIOR__;
	return OTRUE;
}

OBehavior* OInteger_behavior() {
	return &__BEHAVIOR__;
}
