#include <obin.h>

#define __TypeName__ "__Char__"

static OBehavior __BEHAVIOR__ = {0};

static OAny __STRINGS_CACHE__[OCHAR_MAX];

#ifdef ODEBUG
#define _CHECK_SELF_TYPE(S, self, method) \
	if(!OAny_isChar(self))\
		return oraise(S, oerrors(S)->TypeError, \
				__TypeName__"."#method "call from other type", self); \

#define _CHECK_SELF_TYPE_AND_PANIC(self, method) \
		if(!OAny_isChar(self)) \
			opanic(__TypeName__"."#method "call from other type"); \

#else
#define _CHECK_SELF_TYPE(S, self, method)
#define _CHECK_SELF_TYPE_AND_PANIC(self, method)
#endif

#define _value(any) OAny_charVal(any)

OAny OCharacter(ochar ch) {
	OAny result;
	result = OAny_new(EOBIN_TYPE_CHAR);
	OAny_charVal(result) = ch;
	return result;
}

OAny _OCharacter_toString(OState* S, OAny self) {
	ochar temp[2];

	temp[0] = _value(self);
	temp[1] = '\0';
	return OString(S, (ostring)temp);
}

OAny OCharacter_toString(OState* S, OAny self) {
	_CHECK_SELF_TYPE(S, self, OCharacter_toString);

	/*Check for future unicode*/
	if(_value(self) < 0 || _value(self) > OCHAR_MAX) {
		return _OCharacter_toString(S, self);
	}

	return __STRINGS_CACHE__[_value(self)];
}

OAny OCharacter_toInteger(OAny self) {
	_CHECK_SELF_TYPE_AND_PANIC(self, OCharacter_toInteger);
	return OInteger((oint) _value(self));
}

OAny OCharacter_toFloat(OAny self){
	_CHECK_SELF_TYPE_AND_PANIC(self, OCharacter_toFloat);
	return OFloat((ofloat) _value(self));
}

OAny OCharacter_toLower(OState* S, OAny self) {
	_CHECK_SELF_TYPE(S, self, OCharacter_toLower);
	return OCharacter(__otolower(_value(self)));
}

OAny OCharacter_toUpper(OState* S, OAny self) {
	_CHECK_SELF_TYPE(S, self, OCharacter_toUpper);
	return OCharacter(__otoupper(_value(self)));
}

OAny OCharacter_isAlphanum(OState* S, OAny self){
	_CHECK_SELF_TYPE(S, self, OCharacter_isAlphanum);
	return OBool(__oisalpha(_value(self)) || __oisdigit(_value(self)));
}

OAny OCharacter_isAlpha(OState* S, OAny self) {
	_CHECK_SELF_TYPE(S, self, OCharacter_isAlpha);
	return OBool(__oisalpha(_value(self)));
}

OAny OCharacter_isDigit(OState* S, OAny self) {
	_CHECK_SELF_TYPE(S, self, OCharacter_isDigit);
	return OBool(__oisdigit(_value(self)));
}

OAny OCharacter_isLower(OState* S, OAny self) {
	_CHECK_SELF_TYPE(S, self, OCharacter_isLower);
	return OBool(__oislower(_value(self)));
}

OAny OCharacter_isUpper(OState* S, OAny self) {
	_CHECK_SELF_TYPE(S, self, OCharacter_isUpper);
	return OBool(__oisupper(_value(self)));
}

OAny OCharacter_isPunctuation(OState* S, OAny self){
	_CHECK_SELF_TYPE(S, self, OCharacter_isAlpha);
	return OBool(__oispunct(_value(self)));
}

OAny OCharacter_isSpace(OState* S, OAny self) {
	_CHECK_SELF_TYPE(S, self, OCharacter_isSpace);
	return OBool(__oisspace(_value(self)));
}

static OAny __tobool__(OState* S, OAny self) {
	_CHECK_SELF_TYPE(S, self, __tobool__);
	return ObinTrue;
}

static OAny __clone__(OState* S, OAny self) {
	_CHECK_SELF_TYPE(S, self, __clone__);
	return self;
}

static OAny __compare__(OState* S, OAny self, OAny arg1) {
	_CHECK_SELF_TYPE(S, self, __compare__);
	return ocompare(S, OCharacter_toInteger(self), otointeger(S, arg1));
}

static OAny __hash__(OState* S, OAny self){
	_CHECK_SELF_TYPE(S, self, __hash__);
	return OCharacter_toInteger(self);
}

static OAny __tointeger__(OState* S, OAny self){
	_CHECK_SELF_TYPE(S, self, __tointeger__);
	return OCharacter_toInteger(self);
}

static OAny __tofloat__(OState* S, OAny self){
	_CHECK_SELF_TYPE(S, self, __tofloat__);
	return OCharacter_toFloat(self);
}

static void _init_repr_cache(OState* S) {
	int c = 0;

	for(c=0; c<=OCHAR_MAX; c++) {
		__STRINGS_CACHE__[c] = _OCharacter_toString(S, OCharacter(c));
	}
}

obool ocharacter_init(OState* S) {
	_init_repr_cache(S);
	__BEHAVIOR__.__tostring__ = &OCharacter_toString;
	__BEHAVIOR__.__tobool__ = __tobool__;
	__BEHAVIOR__.__clone__ = __clone__;
	__BEHAVIOR__.__hash__ = __hash__;
	__BEHAVIOR__.__compare__ = __compare__;
	__BEHAVIOR__.__tointeger__ = __tointeger__;
	__BEHAVIOR__.__tofloat__ = __tofloat__;

	obehaviors(S)->Character = &__BEHAVIOR__;
	return OTRUE;
}
