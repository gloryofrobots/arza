#include <obin.h>

#define __TypeName__ "__String__"

static ObinBehavior __BEHAVIOR__ = {0};

static obin_byte* __CHARS__[SCHAR_MAX] = {0};

#define _CHECK_SELF_TYPE(state, self, method) \
	if(!obin_any_is_string(self)) { \
		return obin_raise(state, obin_errors(state)->TypeError, \
				__TypeName__"."#method "call from other type", self); \
	} \

static ObinAny _obin_string_empty(ObinState* state) {
	ObinAny result;

	result = obin_char_new(0);
	result.data.char_value.size = 0;
	return result;
}

typedef struct {
	OBIN_CELL_HEADER;
	obin_char* data;
	obin_mem_t capacity;
	obin_mem_t size;
	obin_integer hash;
} ObinString;

#define _string(any) ((ObinString*) OAny_toCell(any))

static obin_char* _string_data(ObinAny any) {
	switch(any.type) {
	case EOBIN_TYPE_STRING:
		return  _string(any)->data;
		break;
	case EOBIN_TYPE_CHAR:
		obin_panic("CHAR TYPE ARE NOT MUTABLE");
		return NULL;
		break;
	default:
		return NULL;
	}
}
static obin_string _string_const_data(ObinAny any) {
	switch(any.type) {
	case EOBIN_TYPE_STRING:
		return  _string(any)->data;
		break;
	case EOBIN_TYPE_CHAR:
		return (obin_string)__CHARS__[any.data.char_value.char_data];
		break;
	default:
		return NULL;
	}
}

/* SIZE FOR BUFFER IN STACK USED TO WRITE INTS AND FLOATS TO STRING */

static obin_integer _string_size(ObinAny any) {
	switch(any.type) {
	case EOBIN_TYPE_STRING:
		return _string(any)->size;
		break;
	case EOBIN_TYPE_CHAR:
		return any.data.char_value.size;
		break;
	default:
		return -1;
	}
}

#define _is_char(any) (any.type == EOBIN_TYPE_CHAR)
#define _is_string(any) (any.type == EOBIN_TYPE_STRING)
#define _is_empty(any) (_is_char(any) && any.data.char_value.size == 0)

/**********************************  TYPETRAIT ***********************************************/

static ObinAny __tostring__(ObinState* state, ObinAny self) {
	return obin_clone(state, self);
}

static ObinAny __tobool__(ObinState* state, ObinAny self) {
	return obin_bool_new(!_is_empty(self));
}

static ObinAny __length__(ObinState* state, ObinAny self) {
	_CHECK_SELF_TYPE(state, self, __length__);

	if(_is_char(self)){
		if(_is_empty(self)){
			return obin_integer_new(0);
		}
		return obin_integer_new(1);
	}

	return obin_integer_new(_string_size(self));
}

static ObinAny __hasitem__(ObinState* state, ObinAny self, ObinAny character) {
	ObinAny result;
	_CHECK_SELF_TYPE(state, self, __hasitem__);

	result = obin_string_index_of(state, self, character, ObinNil, ObinNil);

	return obin_equal(state, result, obin_integers(state)->NotFound);
}

static ObinAny __getitem__(ObinState* state, ObinAny self, ObinAny key) {
	obin_mem_t index;
	obin_char result;
	_CHECK_SELF_TYPE(state, self, __item__);

	if(!obin_any_is_integer(key)){
		return obin_raise(state, obin_errors(state)->TypeError,
				"String.__item__ key must be integer", key);
	}

	index = obin_any_integer(key);
	if(index < 0 || index >= _string_size(self)) {
		return obin_raise(state, obin_errors(state)->TypeError,
				"String.__item__ invalid index", key);
	}

	result = _string_const_data(self)[index];
	return obin_char_new(result);
}

static ObinAny __compare__(ObinState* state, ObinAny self, ObinAny other) {
	obin_mem_t result;
	_CHECK_SELF_TYPE(state, self, __compare__);

	if (!obin_any_is_string(other)) {
		return obin_raise(state, obin_errors(state)->TypeError,
				"String.__compare__ argument is not string", other);
	}

	if (_string_size(self) < _string_size(other)) {
		return obin_integers(state)->Lesser;
	}

	if (_string_size(self) > _string_size(other)) {
		return obin_integers(state)->Greater;
	}

	result = obin_strncmp(_string_const_data(self), _string_const_data(other),
			_string_size(self));

	if (result < 0) {
		return obin_integers(state)->Lesser;
	}
	if (result > 0) {
		return obin_integers(state)->Greater;
	}

	return obin_integers(state)->Equal;
}

static ObinAny __hash__(ObinState* state, ObinAny self) {
	register obin_integer hash = 0;
	register const obin_char * cursor = 0;
	register obin_integer length = 0;
	ObinHashSecret secret;

	_CHECK_SELF_TYPE(state, self, __hash__);

	if(_is_empty(self)){
		return obin_integer_new(0);
	}

	if(_is_char(self)) {
		return obin_integer_new((obin_integer) _string_const_data(self)[0]);
	}

	/* return already hashed value */
	hash = _string(self)->hash;
	if(hash){
		return obin_integer_new(hash);
	}

	secret = obin_hash_secret();
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
	return obin_integer_new(hash);
}

static ObinAny __iterator__(ObinState* state, ObinAny self) {
	return obin_sequence_iterator_new(state, self);
}

static ObinAny __clone__(ObinState* state, ObinAny self) {
	return obin_string_from_carray(state, _string_const_data(self), _string_size(self));
}

static ObinAny _obin_string_blank(ObinState* state, obin_mem_t length);

static ObinAny __add__(ObinState* state, ObinAny str1, ObinAny str2) {
	obin_char* data;
	obin_mem_t size;
	ObinAny result;

	_CHECK_SELF_TYPE(state, str1, __add__);

	if(!obin_any_is_string(str2)) {
		return obin_raise(state, obin_errors(state)->TypeError,
						"String.__add__ invalid argument type, String expected ", str2);
	}

	if (_string_size(str1) == 0) {
		return obin_clone(state, str2);
	}
	if (_string_size(str2) == 0) {
		return obin_clone(state, str1);
	}

	size = _string_size(str1) + _string_size(str2);

	if (size == 0) {
		return obin_strings(state)->Empty;
	}

	if (size == 1) {
		return obin_char_new(
				_string_size(str1) == 0 ?
						_string_const_data(str2)[0] : _string_const_data(str1)[0]);
	}

	result = _obin_string_blank(state, size);
	data = _string_data(result);
	obin_memcpy(data, _string_const_data(str1), _string_size(str1));
	obin_memcpy(data + _string_size(str1), _string_const_data(str2),
			_string_size(str2));

	return result;
}



/***********************************************************************************/
/* constructors */
ObinAny obin_string_new(ObinState* state, obin_string data) {
	int len;

	len = obin_strlen(data);
	if (len == 0) {
		return obin_string_from_carray(state, 0, 0);
	}

	return obin_string_from_carray(state, (obin_char*) data, len);
}

ObinAny obin_char_new(obin_char ch) {
	ObinAny result;

	result = obin_any_new();
	result.type = EOBIN_TYPE_CHAR;
	result.data.char_value.char_data = ch;
	result.data.char_value.size = 1;
	return result;
}

static ObinAny _obin_string_from_carr(ObinState* state, obin_string data, obin_mem_t size) {
	obin_mem_t capacity, body_size;
	ObinString* self;

	body_size = sizeof(ObinString);
	capacity = body_size + size + 1;
	self = (ObinString*) obin_allocate_cell(state, capacity);

	self->capacity = capacity;
	self->size = size;
	self->data = (obin_char*) self + body_size;
	if(data != NULL) {
		obin_memcpy(self->data, data, self->size);
	}

	self->data[self->size] = '\0';

	return obin_cell_new(EOBIN_TYPE_STRING, (OCell*) self, &__BEHAVIOR__, obin_cells(state)->__String__);
}

static ObinAny _obin_string_blank(ObinState* state, obin_mem_t length) {
	return _obin_string_from_carr(state, NULL, length);
}

/*@param data array without \0
 *@param size array size
 */
ObinAny obin_string_from_carray(ObinState* state, obin_string data,
obin_mem_t size) {
	/*empty string*/
	if (size == 0) {
		return _obin_string_empty(state);
	}
	if (size == 1) {
		return obin_char_new(data[0]);
	}

	return _obin_string_from_carr(state, data, size);
}


/* ******************** ATTRIBUTES ***********************************************/
obin_string obin_string_cstr(ObinState* state, ObinAny self){
	return _string_const_data(self);
}

ObinAny obin_string_is_empty(ObinState* state, ObinAny self){
	if(!obin_any_is_string(self)) {
		return obin_raise(state, obin_errors(state)->InternalError,
				"obin_string_is_empty call from other type", self);
	}
	return obin_tobool(state, __length__(state, self));
}
/******************************** MODIFICATIONS *************************************/
/*  function for modify char arrays , return 0 for stop iteration */
typedef int (*_string_modifier)(obin_char* char_data, obin_mem_t index);

/* clone string and modify it`s content by modifier */
ObinAny _clone_and_modify(ObinState* state, ObinAny self,
		_string_modifier modify) {
	ObinAny clone;
	obin_mem_t i;
	if(_is_empty(self)) {
		return self;
	}
	if(_is_char(self)) {
		clone = self;
		/**Tricky part we send pointer to char value wit 0 index*/
		clone.data.char_value.char_data = modify((obin_char*)&clone.data.char_value.char_data, 0);
		return clone;
	}

	clone = __clone__(state, self);

	for (i = 0; i < _string_size(clone); i++) {
		if (modify(_string_data(clone), i) == OFALSE) {
			break;
		}
	}

	return clone;
}

/*********************** CAPITALIZE *************************/
static int _capitalize_modify(obin_char* data, obin_mem_t index) {
	if (!isalpha(data[index])) {
		return OTRUE;
	}

	data[index] = toupper(data[index]);
	return OFALSE;
}

ObinAny obin_string_capitalize(ObinState* state, ObinAny self) {
	static _string_modifier modifier = &_capitalize_modify;
	_CHECK_SELF_TYPE(state, self, capitalize);

	return _clone_and_modify(state, self, modifier);
}

/*********************** CAPITALIZE WORDS*************************/
static int _capitalize_words_modify(obin_char* data, obin_mem_t index) {
	if ((index == 0 || isspace(data[index - 1])) && isalpha(data[index])) {
		data[index] = toupper(data[index]);
	}
	return OTRUE;
}

ObinAny obin_string_capitalize_words(ObinState* state, ObinAny self) {
	static _string_modifier modifier = _capitalize_words_modify;
	_CHECK_SELF_TYPE(state, self, capitalize_words);

	return _clone_and_modify(state, self, modifier);
}
/********************* UPPERCASE *************************/
static int _uppercase_modify(obin_char* data, obin_mem_t index) {
	data[index] = toupper(data[index]);
	return OTRUE;
}

ObinAny obin_string_to_uppercase(ObinState* state, ObinAny self) {
	static _string_modifier modifier = _uppercase_modify;
	_CHECK_SELF_TYPE(state, self, to_uppercase);

	return _clone_and_modify(state, self, modifier);
}

/********************* LOWERCASE ***************************/
static int _lowercase_modify(obin_char* data, obin_mem_t index) {
	data[index] = tolower(data[index]);
	return OTRUE;
}

ObinAny obin_string_to_lowercase(ObinState* state, ObinAny self) {
	static _string_modifier modifier = _lowercase_modify;
	_CHECK_SELF_TYPE(state, self, to_lowercase);

	return _clone_and_modify(state, self, modifier);
}

/************** CONDITIONS **************************************/
/*  function for checking string content by some condition*/
typedef int (*_string_condition)(obin_string char_data, obin_mem_t index);

/* check string content for condition */
ObinAny _check_condition(ObinState* state, ObinAny self,
		_string_condition condition) {
	obin_mem_t i;

	for (i = 0; i < _string_size(self); i++) {
		if (condition(_string_const_data(self), i) == OFALSE) {
			return ObinFalse;
		}
	}

	return ObinTrue;
}
/*************************** IS_ALL_ALPHANUM **********************************/
static int _is_alphanum_condition(obin_string data, obin_mem_t index) {
	return isdigit(data[index]) || isalpha(data[index]);
}

ObinAny obin_string_is_alphanum(ObinState* state, ObinAny self) {
	_CHECK_SELF_TYPE(state, self, is_alphanum);

	return _check_condition(state, self, &_is_alphanum_condition);
}

/*************************** ISALPHA **********************************/
static int _is_alpha_condition(obin_string data, obin_mem_t index) {
	return isalpha(data[index]);
}

ObinAny obin_string_is_alpha(ObinState* state, ObinAny self) {
	_CHECK_SELF_TYPE(state, self, is_alpha);
	return _check_condition(state, self, &_is_alpha_condition);
}

/*************************** ISDIGIT **********************************/
static int _is_digit_condition(obin_string data, obin_mem_t index) {
	return isdigit(data[index]);
}

ObinAny obin_string_is_digit(ObinState* state, ObinAny self) {
	_CHECK_SELF_TYPE(state, self, is_digit);
	return _check_condition(state, self, &_is_digit_condition);
}
/*************************** IS LOWER **********************************/
static int _is_lower_condition(obin_string data, obin_mem_t index) {
	char ch = data[index];
	if(!isalpha(ch)) {
		/*skip other stuff*/
		return 1;
	}

	return islower(ch);
}

ObinAny obin_string_is_lower(ObinState* state, ObinAny self) {
	_CHECK_SELF_TYPE(state, self, is_lower);
	return _check_condition(state, self, &_is_lower_condition);
}
/*************************** IS UPPER **********************************/
static int _is_upper_condition(obin_string data, obin_mem_t index) {
	char ch = data[index];
	if(!isalpha(ch)) {
		/*skip other stuff*/
		return 1;
	}

	return isupper(ch);
}

ObinAny obin_string_is_upper(ObinState* state, ObinAny self) {
	_CHECK_SELF_TYPE(state, self, is_upper);
	return _check_condition(state, self, &_is_upper_condition);
}
/*************************** IS SPACE **********************************/
static int _is_space_condition(obin_string data, obin_mem_t index) {
	return isspace(data[index]);
}

ObinAny obin_string_is_space(ObinState* state, ObinAny self) {
	_CHECK_SELF_TYPE(state, self, is_space);
	return _check_condition(state, self, &_is_space_condition);
}
/************************* SEARCH ***************************************/
typedef ObinAny (*_string_finder)(ObinState* state, ObinAny haystack, ObinAny needle,
obin_mem_t start, obin_mem_t end);

ObinAny _obin_string_find(ObinState* state, ObinAny haystack, ObinAny needle,
		ObinAny start, ObinAny end, _string_finder finder) {
	obin_mem_t pstart;
	obin_mem_t pend;
	obin_mem_t haystack_size;

	haystack_size = _string_size(haystack);
	if (obin_any_is_nil(start)) {
		pstart = 0;
	} else {
		if (obin_any_integer(start) < 0
				|| obin_any_integer(start) > haystack_size) {

			return obin_raise(state, obin_errors(state)->RangeError,
					"String.search Invalid start index for search ", start);
		}

		pstart = (obin_mem_t) obin_any_integer(start);
	}

	if (obin_any_is_nil(end)) {
		pend = haystack_size;
	} else {
		if (obin_any_integer(end) < 0 || obin_any_integer(end) > haystack_size
				|| obin_any_integer(end) < pstart) {

			return obin_raise(state, obin_errors(state)->RangeError,
					"String.search Invalid end index for search ", end);
		}

		pend = (obin_mem_t) obin_any_integer(end);
	}

	if ((pend - pstart) > _string_size(haystack)) {
		return obin_raise(state, obin_errors(state)->RangeError,
					"String.search Invalid search range ",
					obin_tuple_pack(state, 2,
							obin_integer_new(pstart), obin_integer_new(pend)));
	}

	return finder(state, haystack, needle, pstart, pend);
}
/* ****************************** INDEXOF *************************************************************/
ObinAny _string_finder_left(ObinState* state, ObinAny haystack, ObinAny needle,
										obin_mem_t start, obin_mem_t end) {
	obin_mem_t size_h;
	obin_mem_t size_n;
	obin_mem_t i;
	obin_mem_t hi;
	obin_mem_t ni;
	const obin_char* data_h;
    const obin_char* data_n;

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
			return obin_integer_new(i);
		}
		/* Didn't match here.  Try again further along haystack. */
	}

	return obin_integers(state)->NotFound;
}

ObinAny obin_string_index_of(ObinState* state, ObinAny self, ObinAny other,
		ObinAny start, ObinAny end) {
	_CHECK_SELF_TYPE(state, self, index_of);

	if(!obin_any_is_string(other)) {
		return obin_raise(state, obin_errors(state)->TypeError,
				"String.indexof invalid argument type, string expected ", other);
	}

	return _obin_string_find(state, self, other, start, end,
			&_string_finder_left);
}

/* ****************************** LASTINDEXOF *************************************************************/
/*
 Return the highest index in the string
 where substring sub is found, such that sub is contained
 within s[start:end]. Optional arguments start and end
 are interpreted as in slice notation. Return STRING_INDEX_NOT_FOUND on failure.
 */
ObinAny _string_finder_right(ObinState* state, ObinAny haystack, ObinAny needle,
obin_mem_t start, obin_mem_t end) {
	obin_mem_t i;
	obin_mem_t hi;
	obin_mem_t ni;
	const obin_char* data_h;
    const obin_char* data_n;

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
			return obin_integer_new(i - _string_size(needle) + 1);
		}
		/* Didn't match here.  Try again further along haystack. */
	}

	return obin_integers(state)->NotFound;
}

ObinAny obin_string_last_index_of(ObinState* state, ObinAny self, ObinAny other,
		ObinAny start, ObinAny end) {
	_CHECK_SELF_TYPE(state, self, last_index_of);

	if(!obin_any_is_string(other)) {
		return obin_raise(state, obin_errors(state)->TypeError,
				"String.last_indexof invalid argument type, string expected ", other);
	}

	return _obin_string_find(state, self, other, start, end,
			&_string_finder_right);
}

/*********************** BUILDERS *******************************************/
/* TODO IMPLEMENT */
/*ObinAny obin_string_format(ObinState* state, ObinAny format, ...);*/

ObinAny obin_string_dublicate(ObinState* state, ObinAny self, ObinAny _count) {
	obin_mem_t size;
	obin_mem_t count;
	obin_char* data;
	ObinAny result;

	_CHECK_SELF_TYPE(state, self, dublicate);

	if(_is_empty(self)) {
		return self;
	}

	if (obin_any_is_nil(_count)) {
		return obin_clone(state, self);
	}

	if(!obin_any_is_integer(_count)) {
		return obin_raise(state, obin_errors(state)->TypeError,
				"String.dublicate invalid argument type, integer expected ", _count);
	}

	count = obin_any_integer(_count);

	size = _string_size(self) * count;
	result = _obin_string_blank(state, size);
	data = _string_data(result);
	for (; count > 0; count--, data += _string_size(self)) {
		obin_memcpy(data, _string_const_data(self), _string_size(self));
	}

	return result;
}

ObinAny obin_string_split(ObinState* state, ObinAny self, ObinAny separator) {
	ObinAny result;
	ObinAny curPos;
	obin_mem_t current;
	obin_mem_t previous;

	_CHECK_SELF_TYPE(state, self, split);

	if(!obin_any_is_string(separator)) {
		return obin_raise(state, obin_errors(state)->TypeError,
						"String.split invalid argument type, String expected ", separator);
	}

	result = obin_array_new(state, ObinNil);

	if (_string_size(separator) > _string_size(self)) {
		/*can`t split */
		obin_array_push(state, result, obin_clone(state, self));
		return result;
	}

	current = 0;
	previous = 0;

	while (OTRUE) {
		curPos = _string_finder_left(state, self, separator, previous, _string_size(self));

		if (obin_any_is_true(obin_equal(state, curPos, obin_integers(state)->NotFound))) {

			obin_array_push(state, result,
						obin_string_from_carray(state, _string_const_data(self) + previous,
								_string_size(self) - previous));
			return result;
		}
		current = obin_any_integer(curPos);
		if (current == 0) {
			previous = current + _string_size(separator);
			continue;
		}

		obin_array_push(state, result,
				obin_string_from_carray(state, _string_const_data(self) + previous,
						current - previous));

		previous = current + _string_size(separator);
	}

	return result;
}

ObinAny obin_string_join(ObinState* state, ObinAny self, ObinAny collection) {
	ObinAny iterator;
	ObinAny value;
	ObinAny result;
	obin_index counter;

	_CHECK_SELF_TYPE(state, self, join);

	result = obin_strings(state)->Empty;

	counter = obin_any_integer(obin_length(state, collection));
	if(counter==0) {
		return result;
	}

	iterator = obin_iterator(state, collection);

	while (OTRUE) {
		/*avoid appending self at end of string*/
		if(!(--counter)){
			break;
		}

		value = obin_next(state, iterator);
		result = __add__(state, result, value);
		result = __add__(state, result, self);
	}

	/*append last element*/
	value = obin_next(state, iterator);
	result = __add__(state, result, value);
	return result;
}

ObinAny obin_string_pack(ObinState* state, obin_index count, ...){
	ObinAny array;
	obin_index i;
	ObinAny item;
    va_list vargs;

	if(!obin_is_fit_to_memsize(count)) {
		return obin_raise(state, obin_errors(state)->TypeError,
						"String.pack invalid argument type, Invalid size", obin_integer_new(count));
	}

	array = obin_array_new(state, obin_integer_new(count));

    va_start(vargs, count);
    for (i = 0; i < count; i++) {
    	item = va_arg(vargs, ObinAny);
    	obin_array_push(state, array, item);
    }

    va_end(vargs);

    return obin_string_join(state, obin_strings(state)->PrintSeparator, array);
}
/* //native
 str.startswith(prefix[, start[, end]])
 str.lstrip([chars])
 str.rstrip([chars])
 str.splitlines([keepends])
 */

ObinBehavior* obin_char_behavior() {
	return &__BEHAVIOR__;
}

static void _init_chars_cache() {
	int c = 0;

	for(c=0; c<=UCHAR_MAX; c++) {
		__CHARS__[c] = obin_calloc(2, sizeof(obin_char));
		__CHARS__[c][0] = c;
		__CHARS__[c][1] = 0;
	}
}
obin_bool obin_module_string_init(ObinState* state) {
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

	obin_behaviors(state)->Char = &__BEHAVIOR__;

	/*strings proto*/
	obin_cells(state)->__String__ =  obin_cell_new(EOBIN_TYPE_CELL,
			obin_new(state, OCell), &__BEHAVIOR__, obin_cells(state)->__Cell__);


	obin_strings(state)->Nil = obin_string_new(state, "Nil");
	obin_strings(state)->True = obin_string_new(state, "True");
	obin_strings(state)->False = obin_string_new(state, "False");
	obin_strings(state)->Nothing = obin_string_new(state, "Nothing");
	obin_strings(state)->PrintSeparator = obin_char_new(OBIN_PRINT_SEPARATOR);
	obin_strings(state)->Empty = _obin_string_empty(state);
	obin_strings(state)->Space = obin_char_new('\32');
	obin_strings(state)->TabSpaces = obin_string_dublicate(state, obin_strings(state)->Space, obin_integer_new(OBIN_COUNT_TAB_SPACES));

	return OTRUE;
}
