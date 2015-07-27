#include <obin.h>

#define __TypeName__ "__String__"

static OBehavior __BEHAVIOR__ = {0};

static obyte* __CHARS__[SCHAR_MAX] = {0};

#define _CHECK_SELF_TYPE(S, self, method) \
	if(!OAny_isString(self)) { \
		return oraise(S, oerrors(S)->TypeError, \
				__TypeName__"."#method "call from other type", self); \
	} \

typedef struct {
	OCELL_HEADER;
	ochar* data;
	omem_t capacity;
	omem_t size;
	oint hash;
} ObinString;

#define _string(any) ((ObinString*) OAny_toCell(any))

static ochar* _string_data(OAny any) {
	switch(any.type) {
	case EOBIN_TYPE_STRING:
		return  _string(any)->data;
	case EOBIN_TYPE_CHAR:
		opanic("CHAR TYPE ARE NOT MUTABLE");
		return NULL;
	default:
		return NULL;
	}
}
static ostring _string_const_data(OAny any) {
	switch(any.type) {
	case EOBIN_TYPE_STRING:
		return  _string(any)->data;
		break;
	case EOBIN_TYPE_CHAR:
		return (ostring)__CHARS__[any.data.char_value];
		break;
	default:
		return NULL;
	}
}

/* SIZE FOR BUFFER IN STACK USED TO WRITE INTS AND FLOATS TO STRING */

static oint _string_size(OAny any) {
	switch(any.type) {
	case EOBIN_TYPE_STRING:
		return _string(any)->size;
		break;
	case EOBIN_TYPE_CHAR:
		return 1;
		break;
	default:
		return -1;
	}
}

#define _is_char(any) (any.type == EOBIN_TYPE_CHAR)
#define _is_string(any) (any.type == EOBIN_TYPE_STRING)
#define _is_empty(any) (_is_string(any) && _string(any)->size == 0)

/**********************************  TYPETRAIT ***********************************************/

static OAny __tostring__(OState* S, OAny self) {
	return oclone(S, self);
}

static OAny __tobool__(OState* S, OAny self) {
	return OBool(!_is_empty(self));
}

static OAny __length__(OState* S, OAny self) {
	_CHECK_SELF_TYPE(S, self, __length__);

	if(_is_char(self)){
		if(_is_empty(self)){
			return OInteger(0);
		}
		return OInteger(1);
	}

	return OInteger(_string_size(self));
}

static OAny __hasitem__(OState* S, OAny self, OAny character) {
	OAny result;
	_CHECK_SELF_TYPE(S, self, __hasitem__);

	result = OString_indexOf(S, self, character, ObinNil, ObinNil);

	return oequal(S, result, ointegers(S)->NotFound);
}

static OAny __getitem__(OState* S, OAny self, OAny key) {
	omem_t index;
	ochar result;
	_CHECK_SELF_TYPE(S, self, __item__);

	if(!OAny_isInt(key)){
		return oraise(S, oerrors(S)->TypeError,
				"String.__item__ key must be integer", key);
	}

	index = OAny_toInt(key);
	if(index < 0 || index >= _string_size(self)) {
		return oraise(S, oerrors(S)->TypeError,
				"String.__item__ invalid index", key);
	}

	result = _string_const_data(self)[index];
	return OChar_new(result);
}

static OAny __compare__(OState* S, OAny self, OAny other) {
	omem_t result;
	_CHECK_SELF_TYPE(S, self, __compare__);

	if (!OAny_isString(other)) {
		return oraise(S, oerrors(S)->TypeError,
				"String.__compare__ argument is not string", other);
	}

	if (_string_size(self) < _string_size(other)) {
		return ointegers(S)->Lesser;
	}

	if (_string_size(self) > _string_size(other)) {
		return ointegers(S)->Greater;
	}

	result = ostrncmp(_string_const_data(self), _string_const_data(other),
			_string_size(self));

	if (result < 0) {
		return ointegers(S)->Lesser;
	}
	if (result > 0) {
		return ointegers(S)->Greater;
	}

	return ointegers(S)->Equal;
}

static OAny __hash__(OState* S, OAny self) {
	register oint hash = 0;
	register const ochar * cursor = 0;
	register oint length = 0;
	OHashSecret secret;

	_CHECK_SELF_TYPE(S, self, __hash__);

	if(_is_empty(self)){
		return OInteger(0);
	}

	if(_is_char(self)) {
		return OInteger((oint) _string_const_data(self)[0]);
	}

	/* return already hashed value */
	hash = _string(self)->hash;
	if(hash){
		return OInteger(hash);
	}

	secret = ohash_secret();
	cursor = _string_const_data(self);
    hash = secret.prefix;
	hash ^= (*(cursor) << 7);
	length = _string_size(self);
	while(--length >= 0){
		hash = (1000003 * hash) ^ *cursor;
		cursor++;
	}

	hash ^= length;
	hash ^= secret.suffix;

	_string(self)->hash = hash;
	return OInteger(hash);
}

static OAny __iterator__(OState* S, OAny self) {
	return OSequence_iterator(S, self);
}

static OAny __clone__(OState* S, OAny self) {
	return OString_fromCArray(S, _string_const_data(self), _string_size(self));
}

static OAny _obin_string_blank(OState* S, omem_t length);

static OAny __add__(OState* S, OAny str1, OAny str2) {
	ochar* data;
	omem_t size;
	OAny result;

	_CHECK_SELF_TYPE(S, str1, __add__);

	if(!OAny_isString(str2)) {
		return oraise(S, oerrors(S)->TypeError,
						"String.__add__ invalid argument type, String expected ", str2);
	}

	if (_string_size(str1) == 0) {
		return oclone(S, str2);
	}
	if (_string_size(str2) == 0) {
		return oclone(S, str1);
	}

	size = _string_size(str1) + _string_size(str2);

	if (size == 0) {
		return ostrings(S)->Empty;
	}

	if (size == 1) {
		return OChar_new(
				_string_size(str1) == 0 ?
						_string_const_data(str2)[0] : _string_const_data(str1)[0]);
	}

	result = _obin_string_blank(S, size);
	data = _string_data(result);
	omemcpy(data, _string_const_data(str1), _string_size(str1));
	omemcpy(data + _string_size(str1), _string_const_data(str2),
			_string_size(str2));

	return result;
}



/***********************************************************************************/
/* constructors */
OAny OString(OState* S, ostring data) {
	int len;

	len = ostrlen(data);
	if (len == 0) {
		return OString_fromCArray(S, 0, 0);
	}

	return OString_fromCArray(S, (ochar*) data, len);
}

OAny OChar_new(ochar ch) {
	OAny result;

	result = OAny_new();
	result.type = EOBIN_TYPE_CHAR;
	result.data.char_value = ch;
	return result;
}

static OAny _obin_string_from_carr(OState* S, ostring data, omem_t size) {
	omem_t capacity, body_size;
	ObinString* self;

	body_size = sizeof(ObinString);
	capacity = body_size + size + 1;
	self = (ObinString*) omemory_allocate_cell(S, capacity);

	self->capacity = capacity;
	self->size = size;
	self->data = (ochar*) self + body_size;
	if(data != NULL) {
		omemcpy(self->data, data, self->size);
	}

	self->data[self->size] = '\0';

	return OCell_new(EOBIN_TYPE_STRING, (OCell*) self, &__BEHAVIOR__, ocells(S)->__String__);
}

static OAny _obin_string_blank(OState* S, omem_t length) {
	return _obin_string_from_carr(S, NULL, length);
}

/*@param data array without \0
 *@param size array size
 */
OAny OString_fromCArray(OState* S, ostring data,
omem_t size) {
	/*empty string*/
	if (size == 0) {
		return ostrings(S)->Empty;
	}
	if (size == 1) {
		return OChar_new(data[0]);
	}

	return _obin_string_from_carr(S, data, size);
}


/* ******************** ATTRIBUTES ***********************************************/
ostring OString_cstr(OState* S, OAny self){
	return _string_const_data(self);
}

OAny obin_string_is_empty(OState* S, OAny self){
	if(!OAny_isString(self)) {
		return oraise(S, oerrors(S)->InternalError,
				"obin_string_is_empty call from other type", self);
	}
	return otobool(S, __length__(S, self));
}
/******************************** MODIFICATIONS *************************************/
/*  function for modify char arrays , return 0 for stop iteration */
typedef int (*_string_modifier)(ochar* char_data, omem_t index);

/* clone string and modify it`s content by modifier */
OAny _clone_and_modify(OState* S, OAny self,
		_string_modifier modify) {
	OAny clone;
	omem_t i;
	if(_is_empty(self)) {
		return self;
	}
	if(_is_char(self)) {
		clone = self;
		/**Tricky part we send pointer to char value wit 0 index*/
		clone.data.char_value = modify((ochar*)&clone.data.char_value, 0);
		return clone;
	}

	clone = __clone__(S, self);

	for (i = 0; i < _string_size(clone); i++) {
		if (modify(_string_data(clone), i) == OFALSE) {
			break;
		}
	}

	return clone;
}

/*********************** CAPITALIZE *************************/
static int _capitalize_modify(ochar* data, omem_t index) {
	if (!isalpha(data[index])) {
		return OTRUE;
	}

	data[index] = toupper(data[index]);
	return OFALSE;
}

OAny OString_capitalize(OState* S, OAny self) {
	static _string_modifier modifier = &_capitalize_modify;
	_CHECK_SELF_TYPE(S, self, capitalize);

	return _clone_and_modify(S, self, modifier);
}

/*********************** CAPITALIZE WORDS*************************/
static int _capitalize_words_modify(ochar* data, omem_t index) {
	if ((index == 0 || isspace(data[index - 1])) && isalpha(data[index])) {
		data[index] = toupper(data[index]);
	}
	return OTRUE;
}

OAny OString_capitalizeWords(OState* S, OAny self) {
	static _string_modifier modifier = _capitalize_words_modify;
	_CHECK_SELF_TYPE(S, self, capitalize_words);

	return _clone_and_modify(S, self, modifier);
}
/********************* UPPERCASE *************************/
static int _uppercase_modify(ochar* data, omem_t index) {
	data[index] = toupper(data[index]);
	return OTRUE;
}

OAny OString_toUpper(OState* S, OAny self) {
	static _string_modifier modifier = _uppercase_modify;
	_CHECK_SELF_TYPE(S, self, to_uppercase);

	return _clone_and_modify(S, self, modifier);
}

/********************* LOWERCASE ***************************/
static int _lowercase_modify(ochar* data, omem_t index) {
	data[index] = tolower(data[index]);
	return OTRUE;
}

OAny OString_toLower(OState* S, OAny self) {
	static _string_modifier modifier = _lowercase_modify;
	_CHECK_SELF_TYPE(S, self, to_lowercase);

	return _clone_and_modify(S, self, modifier);
}

/************** CONDITIONS **************************************/
/*  function for checking string content by some condition*/
typedef int (*_string_condition)(ostring char_data, omem_t index);

/* check string content for condition */
OAny _check_condition(OState* S, OAny self,
		_string_condition condition) {
	omem_t i;

	for (i = 0; i < _string_size(self); i++) {
		if (condition(_string_const_data(self), i) == OFALSE) {
			return ObinFalse;
		}
	}

	return ObinTrue;
}
/*************************** IS_ALL_ALPHANUM **********************************/
static int _is_alphanum_condition(ostring data, omem_t index) {
	return isdigit(data[index]) || isalpha(data[index]);
}

OAny OString_isAlphanum(OState* S, OAny self) {
	_CHECK_SELF_TYPE(S, self, is_alphanum);

	return _check_condition(S, self, &_is_alphanum_condition);
}

/*************************** ISALPHA **********************************/
static int _is_alpha_condition(ostring data, omem_t index) {
	return isalpha(data[index]);
}

OAny OString_isAlpha(OState* S, OAny self) {
	_CHECK_SELF_TYPE(S, self, is_alpha);
	return _check_condition(S, self, &_is_alpha_condition);
}

/*************************** ISDIGIT **********************************/
static int _is_digit_condition(ostring data, omem_t index) {
	return isdigit(data[index]);
}

OAny OString_isDigit(OState* S, OAny self) {
	_CHECK_SELF_TYPE(S, self, is_digit);
	return _check_condition(S, self, &_is_digit_condition);
}
/*************************** IS LOWER **********************************/
static int _is_lower_condition(ostring data, omem_t index) {
	char ch = data[index];
	if(!isalpha(ch)) {
		/*skip other stuff*/
		return 1;
	}

	return islower(ch);
}

OAny OString_isLower(OState* S, OAny self) {
	_CHECK_SELF_TYPE(S, self, is_lower);
	return _check_condition(S, self, &_is_lower_condition);
}
/*************************** IS UPPER **********************************/
static int _is_upper_condition(ostring data, omem_t index) {
	char ch = data[index];
	if(!isalpha(ch)) {
		/*skip other stuff*/
		return 1;
	}

	return isupper(ch);
}

OAny OString_isUpper(OState* S, OAny self) {
	_CHECK_SELF_TYPE(S, self, is_upper);
	return _check_condition(S, self, &_is_upper_condition);
}
/*************************** IS SPACE **********************************/
static int _is_space_condition(ostring data, omem_t index) {
	return isspace(data[index]);
}

OAny OString_isSpace(OState* S, OAny self) {
	_CHECK_SELF_TYPE(S, self, is_space);
	return _check_condition(S, self, &_is_space_condition);
}
/************************* SEARCH ***************************************/
typedef OAny (*_string_finder)(OState* S, OAny haystack, OAny needle,
omem_t start, omem_t end);

OAny _obin_string_find(OState* S, OAny haystack, OAny needle,
		OAny start, OAny end, _string_finder finder) {
	omem_t pstart;
	omem_t pend;
	omem_t haystack_size;

	haystack_size = _string_size(haystack);
	if (OAny_isNil(start)) {
		pstart = 0;
	} else {
		if (OAny_toInt(start) < 0
				|| OAny_toInt(start) > haystack_size) {

			return oraise(S, oerrors(S)->RangeError,
					"String.search Invalid start index for search ", start);
		}

		pstart = (omem_t) OAny_toInt(start);
	}

	if (OAny_isNil(end)) {
		pend = haystack_size;
	} else {
		if (OAny_toInt(end) < 0 || OAny_toInt(end) > haystack_size
				|| OAny_toInt(end) < pstart) {

			return oraise(S, oerrors(S)->RangeError,
					"String.search Invalid end index for search ", end);
		}

		pend = (omem_t) OAny_toInt(end);
	}

	if ((pend - pstart) > _string_size(haystack)) {
		return oraise(S, oerrors(S)->RangeError,
					"String.search Invalid search range ",
					OTuple(S, 2,
							OInteger(pstart), OInteger(pend)));
	}

	return finder(S, haystack, needle, pstart, pend);
}
/* ****************************** INDEXOF *************************************************************/
OAny _string_finder_left(OState* S, OAny haystack, OAny needle,
										omem_t start, omem_t end) {
	omem_t size_h;
	omem_t size_n;
	omem_t i;
	omem_t hi;
	omem_t ni;
	const ochar* data_h;
    const ochar* data_n;

    data_h = _string_const_data(haystack);
    data_n = _string_const_data(needle);
    size_h = _string_size(haystack);
    size_n = _string_size(needle);

	for (i = start; i < end; i++) {
		/*Is the needle at this point in the haystack?*/
		hi = i;
		ni = 0;
		while(ni < size_n && hi < size_h
				&& (data_h[hi]==data_n[ni]) ){
			ni++;
			hi++;
		}
		if (ni == size_n) {
			/* Found match! */
			return OInteger(i);
		}
		/* Didn't match here.  Try again further along haystack. */
	}

	return ointegers(S)->NotFound;
}

OAny OString_indexOf(OState* S, OAny self, OAny other,
		OAny start, OAny end) {
	_CHECK_SELF_TYPE(S, self, index_of);

	if(!OAny_isString(other)) {
		return oraise(S, oerrors(S)->TypeError,
				"String.indexof invalid argument type, string expected ", other);
	}

	return _obin_string_find(S, self, other, start, end,
			&_string_finder_left);
}

/* ****************************** LASTINDEXOF *************************************************************/
/*
 Return the highest index in the string
 where substring sub is found, such that sub is contained
 within s[start:end]. Optional arguments start and end
 are interpreted as in slice notation. Return STRING_INDEX_NOT_FOUND on failure.
 */
OAny _string_finder_right(OState* S, OAny haystack, OAny needle,
omem_t start, omem_t end) {
	omem_t i;
	omem_t hi;
	omem_t ni;
	const ochar* data_h;
    const ochar* data_n;

    data_h = _string_const_data(haystack);
    data_n = _string_const_data(needle);
	for (i = end - 1; i >= start; i--) {
		/*for is to creepy in that case, while is more readable */
		hi = i;
		ni = _string_size(needle) - 1;
		while (hi >= start && ni > 0 && (data_h[hi] == data_n[ni])) {
				--hi;
				--ni;
		}

		if (ni == 0) {
			/*Found match! */
			return OInteger(i - _string_size(needle) + 1);
		}
		/* Didn't match here.  Try again further along haystack. */
	}

	return ointegers(S)->NotFound;
}

OAny OString_lastIndexOf(OState* S, OAny self, OAny other,
		OAny start, OAny end) {
	_CHECK_SELF_TYPE(S, self, last_index_of);

	if(!OAny_isString(other)) {
		return oraise(S, oerrors(S)->TypeError,
				"String.last_indexof invalid argument type, string expected ", other);
	}

	return _obin_string_find(S, self, other, start, end,
			&_string_finder_right);
}

/*********************** BUILDERS *******************************************/
/* TODO IMPLEMENT */
/*ObinAny obin_string_format(ObinState* S, ObinAny format, ...);*/

OAny OString_dublicate(OState* S, OAny self, OAny _count) {
	omem_t size;
	omem_t count;
	ochar* data;
	OAny result;

	_CHECK_SELF_TYPE(S, self, dublicate);

	if(_is_empty(self)) {
		return self;
	}

	if (OAny_isNil(_count)) {
		return oclone(S, self);
	}

	if(!OAny_isInt(_count)) {
		return oraise(S, oerrors(S)->TypeError,
				"String.dublicate invalid argument type, integer expected ", _count);
	}

	count = OAny_toInt(_count);

	size = _string_size(self) * count;
	result = _obin_string_blank(S, size);
	data = _string_data(result);
	for (; count > 0; count--, data += _string_size(self)) {
		omemcpy(data, _string_const_data(self), _string_size(self));
	}

	return result;
}

OAny OString_split(OState* S, OAny self, OAny separator) {
	OAny result;
	OAny curPos;
	omem_t current;
	omem_t previous;

	_CHECK_SELF_TYPE(S, self, split);

	if(!OAny_isString(separator)) {
		return oraise(S, oerrors(S)->TypeError,
						"String.split invalid argument type, String expected ", separator);
	}

	result = OArray(S, ObinNil);

	if (_string_size(separator) > _string_size(self)) {
		/*can`t split */
		OArray_push(S, result, oclone(S, self));
		return result;
	}

	current = 0;
	previous = 0;

	while (OTRUE) {
		curPos = _string_finder_left(S, self, separator, previous, _string_size(self));

		if (OAny_isTrue(oequal(S, curPos, ointegers(S)->NotFound))) {

			OArray_push(S, result,
						OString_fromCArray(S, _string_const_data(self) + previous,
								_string_size(self) - previous));
			return result;
		}
		current = OAny_toInt(curPos);
		if (current == 0) {
			previous = current + _string_size(separator);
			continue;
		}

		OArray_push(S, result,
				OString_fromCArray(S, _string_const_data(self) + previous,
						current - previous));

		previous = current + _string_size(separator);
	}

	return result;
}

OAny OString_join(OState* S, OAny self, OAny collection) {
	OAny iterator;
	OAny value;
	OAny result;
	oindex_t counter;

	_CHECK_SELF_TYPE(S, self, join);

	result = ostrings(S)->Empty;

	counter = OAny_toInt(olength(S, collection));
	if(counter==0) {
		return result;
	}

	iterator = oiterator(S, collection);

	while (OTRUE) {
		/*avoid appending self at end of string*/
		if(!(--counter)){
			break;
		}

		value = onext(S, iterator);
		result = __add__(S, result, value);
		result = __add__(S, result, self);
	}

	/*append last element*/
	value = onext(S, iterator);
	result = __add__(S, result, value);
	return result;
}

OAny OString_pack(OState* S, oindex_t count, ...){
	OAny array;
	oindex_t i;
	OAny item;
    va_list vargs;

	if(!OBIN_IS_FIT_TO_MEMSIZE(count)) {
		return oraise(S, oerrors(S)->TypeError,
						"String.pack invalid argument type, Invalid size", OInteger(count));
	}

	array = OArray(S, OInteger(count));

    va_start(vargs, count);
    for (i = 0; i < count; i++) {
    	item = va_arg(vargs, OAny);
    	OArray_push(S, array, item);
    }

    va_end(vargs);

    return OString_join(S, ostrings(S)->PrintSeparator, array);
}
/* //native
 str.startswith(prefix[, start[, end]])
 str.lstrip([chars])
 str.rstrip([chars])
 str.splitlines([keepends])
 */

OBehavior* obin_char_behavior() {
	return &__BEHAVIOR__;
}

static void _init_chars_cache() {
	int c = 0;

	for(c=0; c<=UCHAR_MAX; c++) {
		__CHARS__[c] = ocalloc(2, sizeof(ochar));
		__CHARS__[c][0] = c;
		__CHARS__[c][1] = 0;
	}
}

obool ostring_init(OState* S) {
	_init_chars_cache();

	__BEHAVIOR__.__name__ = "__String__";
	__BEHAVIOR__.__tostring__ = __tostring__;
	__BEHAVIOR__.__tobool__ = __tobool__;
	__BEHAVIOR__.__clone__ = __clone__;
	__BEHAVIOR__.__compare__ = __compare__;
	__BEHAVIOR__.__hash__ = __hash__;

	__BEHAVIOR__.__iterator__ = __iterator__;
	__BEHAVIOR__.__length__ = __length__;
	__BEHAVIOR__.__getitem__ = __getitem__;
	__BEHAVIOR__.__hasitem__ = __hasitem__;
	__BEHAVIOR__.__add__ = __add__;

	obehaviors(S)->Char = &__BEHAVIOR__;

	/*strings proto*/
	ocells(S)->__String__ =  OCell_new(EOBIN_TYPE_CELL,
			obin_new(S, OCell), &__BEHAVIOR__, ocells(S)->__Cell__);


	ostrings(S)->Nil = OString(S, "Nil");
	ostrings(S)->True = OString(S, "True");
	ostrings(S)->False = OString(S, "False");
	ostrings(S)->Nothing = OString(S, "Nothing");
	ostrings(S)->PrintSeparator = OChar_new(OBIN_PRINT_SEPARATOR);
	ostrings(S)->Empty = _obin_string_from_carr(S, "", 0);
	ostrings(S)->Space = OChar_new('\32');
	ostrings(S)->TabSpaces = OString_dublicate(S, ostrings(S)->Space, OInteger(OBIN_COUNT_TAB_SPACES));

	return OTRUE;
}
