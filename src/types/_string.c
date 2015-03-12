#include <stdarg.h>

#include <core/orandom.h>
#include <core/ocontext.h>
#include <core/omemory.h>
#include <core/obuiltin.h>
#include <types/oerror.h>
#include <types/ostring.h>

/* ALIASES */
#define _strlen strlen
#define _strstr strstr
#define _snprintf snprintf
#define _strncmp strncmp
/* SIZE FOR BUFFER IN STACK USED TO WRITE INTS AND FLOATS TO STRING */

#define STRING_INDEX_NOT_FOUND -1
#define OBIN_SPLIT_STRING_DEFAULT_ARRAY_SIZE 8

typedef struct {
	OBIN_CELL_HEADER;
	obin_char* data;
	obin_mem_t capacity;
	obin_mem_t size;
	obin_integer hash;
} ObinString;

#define _string(any) ((ObinString*) obin_any_cell(any))

static obin_char* _string_data(ObinAny any) {
	switch(any.type) {
	case EOBIN_TYPE_STRING:
		return  _string(any)->data;
		break;
	case EOBIN_TYPE_CHAR:
		return any.data.char_value;
		break;
	}
}

static obin_integer _string_size(ObinAny any) {
	switch(any.type) {
	case EOBIN_TYPE_STRING:
		return _string(any)->size;
		break;
	case EOBIN_TYPE_CHAR:
		return any.data.char_value.size;
		break;
	}
}

static obin_integer _string_capacity(ObinAny any) {
	switch(any.type) {
	case EOBIN_TYPE_STRING:
		return  _string(any)->size + 1;
		break;
	case EOBIN_TYPE_CHAR:
		return 1;
		break;
	}
}

#define IS_CHAR(any) (any.type == EOBIN_TYPE_CHAR)
#define IS_STRING(any) (any.type == EOBIN_TYPE_STRING)
#define IS_EMPTY(any) (IS_CHAR(any) && any.data.char_value.size == 0)

/********************************** STRING TYPE TRAIT ***********************************************/

static ObinAny __tostring__(ObinState* state, ObinAny self) {
	return self;
}

static ObinAny __destroy__(ObinState* state, ObinAny self) {
	if(IS_CHAR(self)){
		return ObinNothing;
	}

	if(!IS_STRING(self)) {
		return obin_raise_type_error(state, "String.__destroy__ call from other type", self);
	}

	obin_free(_string_data(self));
	obin_free(obin_any_cell(self));
	return ObinNothing;
}

static ObinAny __length__(ObinState* state, ObinAny self) {
	if(!obin_any_is_string(self)) {
		return obin_raise_type_error(state, "obin_string_length call from other type", self);
	}

	if(IS_CHAR(self)){
		if(IS_EMPTY(self)){
			return 0;
		}
		return 1;
	}

	return obin_integer_new(_string_size(self));
}

static ObinAny __hasitem__(ObinState* state, ObinAny self, ObinAny character) {
	ObinAny result;
	result = obin_string_index_of(state, self, character, ObinNil, ObinNil);

	if(obin_any_integer(result) == STRING_INDEX_NOT_FOUND) {
		return ObinFalse;
	}

	return ObinTrue;
}

static ObinAny __getitem__(ObinState* state, ObinAny self, ObinAny key) {
	obin_mem_t index;
	obin_char result;

	if(!obin_any_is_string(self)) {
		return obin_raise_type_error(state, "String.__item__ call from other type", self);
	}

	if(!obin_any_is_integer(key)){
		return obin_raise_type_error(state, "String.__item__ key must be integer", index);
	}

	index = obin_any_integer(key);
	if(index < 0 || index >= _string_size(self)) {
		return obin_raise_value_error(state, "String.__item__ invalid index", key);
	}

	result = _string_data(self)[index];
	return obin_char_new(state, result);
}

static ObinAny __compare__(ObinState* state, ObinAny self, ObinAny other) {
	obin_mem_t result;

	if(!obin_any_is_string(self)) {
		return obin_raise_type_error(state, "String.__compare__ call from other type", self);
	}

	if (!obin_any_is_string(other)) {
		return obin_raise_type_error(state, "String.__compare__ invalid argument type", other);
	}

	if (_string_size(self) < _string_size(other)) {
		return ObinLesser;
	}

	if (_string_size(self) > _string_size(other)) {
		return ObinGreater;
	}

	result = _strncmp(_string_data(self), _string_data(other),
			_string_size(self));

	if (result < 0) {
		return ObinLesser;
	}
	if (result > 0) {
		return ObinGreater;
	}

	return ObinEqual;
}

static ObinAny __hash__(ObinState* state, ObinAny self) {
	register obin_integer hash = 0;
	register obin_char * cursor = 0;
	register obin_integer length = 0;
	ObinHashSecret secret;

	if(!obin_any_is_string(self)) {
		return obin_raise_type_error(state, "String.__hash__ call from other type", self);
	}

	if(IS_EMPTY(self)){
		return obin_integer_new(0);
	}

	if(IS_CHAR(self)) {
		return obin_integer_new((obin_integer) _string_data(self)[0]);
	}

	/* return already hashed value */
	hash = _string(self)->hash;
	if(hash){
		return obin_integer_new(hash);
	}

	secret = obin_hash_secret();
	cursor = _string_data(self);
    hash = secret.prefix;
	hash ^= (*(cursor) << 7);
	length = _string_length(self);
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
	return obin_string_new_char_array(state, _string_data(self), _string_size(self));
}


static ObinNativeTraits __TRAITS__ = {
	 /*base*/
	 __tostring__,
	 __destroy__,
	 __clone__,
	 __compare__,
	 __hash__,
	 /*collection*/
	 __iterator__,
	 0, /*__next__*/
	 __length__,
	 __getitem__,
	 0, /*__setitem__*/
	 __hasitem__,
	 /* generator */
	 0/*__next__*/
};
/***********************************************************************************/
/* constructors */
ObinAny obin_string_new(ObinState* state, obin_string data) {
	int len;

	len = _strlen(data);
	if (len == 0) {
		return obin_string_new_char_array(state, 0, 0);
	}

	return obin_string_new_char_array(state, data, len);
}

ObinAny obin_char_new(ObinState* state, obin_char ch) {
	ObinAny result;

	result = obin_any_new();
	result.type = EOBIN_TYPE_CHAR;
	result.data.char_value.data[0] = ch;
	result.data.char_value.size = 1;
	return result;
}

ObinAny obin_string_empty(ObinState* state) {
	ObinAny result;

	result = obin_char_new(state, 0);
	result.data.char_value.size = 0;
	return result;
}

static ObinAny _obin_string_new_char_array(ObinState* state, obin_char* data,
obin_mem_t size, obin_bool is_shared) {
	ObinString* self;

	/*empty string*/
	if (size == 0) {
		return obin_string_empty(state);
	}
	if (size == 1) {
		return obin_char_new(state, data[0]);
	}

	self = obin_malloc_type(state, ObinString);
	obin_cell_set_native_traits(self, __TRAITS__);
	self->capacity = size + 1;
	self->size = size;

	if (is_shared == 1) {
		self->data = obin_malloc_collection(state, obin_char,
				self->capacity);
		obin_memcpy(self->data, data, size);
	} else {
		self->data = data;
	}
	self->data[self.size] = '\0';

	return obin_cell_new(EOBIN_TYPE_STRING, self);
}

/*@param data array without \0
 *@param size array size
 */
ObinAny obin_string_new_char_array(ObinState* state, obin_char* data,
obin_mem_t size) {
	return _obin_string_new_char_array(state, data, size, OFALSE);
}


/* ******************** ATTRIBUTES ***********************************************/
ObinAny obin_string_is_empty(ObinState* state, ObinAny self){
	if(!obin_any_is_string(self)) {
		return obin_raise_type_error(state, "obin_string_is_empty call from other type", self);
	}
	return obin_bool_new(
			obin_any_integer(__length__(state, self)) == 0);
}
/******************************** MODIFICATIONS *************************************/
/*  function for modify char arrays , return 0 for stop iteration */
typedef int (*_string_modifier)(obin_string data, obin_mem_t index);

/* clone string and modify it`s content by modifier */
ObinAny _clone_and_modify(ObinState* state, ObinAny self,
		_string_modifier modify) {
	ObinAny clone;
	obin_mem_t i;

	clone = __clone__(state, self);

	for (i = 0; i < _string_size(clone); i++) {
		if (modify(_string_data(clone), i) == OFALSE) {
			break;
		}
	}

	return clone;
}

/*********************** CAPITALIZE *************************/
static int _capitalize_modify(obin_string data, obin_mem_t index) {
	if (!isalpha(data[index])) {
		return OTRUE;
	}

	data[index] = toupper(data[index]);
	return OFALSE;
}

ObinAny obin_string_capitalize(ObinState* state, ObinAny self) {
	static _string_modifier modifier = _capitalize_modify;
	if(!obin_any_is_string(self)) {
		return obin_raise_type_error(state, "obin_string_capitalize call from other type", self);
	}

	return _clone_and_modify(state, self, modifier);
}

/*********************** CAPITALIZE WORDS*************************/
static int _capitalize_words_modify(obin_string data, obin_mem_t index) {
	if ((index == 0 || isspace(data[index - 1])) && isalpha(data[index])) {
		data[index] = toupper(data[index]);
	}
	return OTRUE;
}

ObinAny obin_string_capitalize_words(ObinState* state, ObinAny self) {
	static _string_modifier modifier = _capitalize_words_modify;

	if(!obin_any_is_string(self)) {
		return obin_raise_type_error(state, "obin_string_capitalize_words call from other type", self);
	}

	return _clone_and_modify(state, self, modifier);
}
/********************* UPPERCASE *************************/
static int _uppercase_modify(obin_string data, obin_mem_t index) {
	data[index] = toupper(data[index]);
	return OTRUE;
}

ObinAny obin_string_to_uppercase(ObinState* state, ObinAny self) {
	static _string_modifier modifier = _uppercase_modify;

	if(!obin_any_is_string(self)) {
		return obin_raise_type_error(state, "obin_string_to_uppercase call from other type", self);
	}

	return _clone_and_modify(state, self, modifier);
}

/********************* LOWERCASE ***************************/
static int _lowercase_modify(obin_string data, obin_mem_t index) {
	data[index] = tolower(data[index]);
	return OTRUE;
}

ObinAny obin_string_to_lowercase(ObinState* state, ObinAny self) {
	static _string_modifier modifier = _lowercase_modify;
	if(!obin_any_is_string(self)) {
		return obin_raise_type_error(state, "obin_string_lowercase call from other type", self);
	}

	return _clone_and_modify(state, self, modifier);
}

/************** CONDITIONS **************************************/
/*  function for checking string content by some condition*/
typedef int (*_string_condition)(obin_string data, obin_mem_t index);

/* check string content for condition */
ObinAny _check_condition(ObinState* state, ObinAny self,
		_string_condition condition) {
	obin_mem_t i;

	for (i = 0; i < _string_size(self); i++) {
		if (condition(_string_data(self), i) == OFALSE) {
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
	if(!obin_any_is_string(self)) {
		return obin_raise_type_error(state, "obin_string_is_alphanum call from other type", self);
	}
	return _check_condition(state, self, &_is_alphanum_condition);
}

/*************************** ISALPHA **********************************/
static int _is_alpha_condition(obin_string data, obin_mem_t index) {
	return isalpha(data[index]);
}

ObinAny obin_string_is_alpha(ObinState* state, ObinAny self) {
	if(!obin_any_is_string(self)) {
		return obin_raise_type_error(state, "obin_string_is_alpha call from other type", self);
	}
	return _check_condition(state, self, &_is_alpha_condition);
}

/*************************** ISDIGIT **********************************/
static int _is_digit_condition(obin_string data, obin_mem_t index) {
	return isdigit(data[index]);
}

ObinAny obin_string_is_digit(ObinState* state, ObinAny self) {
	if(!obin_any_is_string(self)) {
		return obin_raise_type_error(state, "obin_string_is_digit call from other type", self);
	}
	return _check_condition(state, self, &_is_digit_condition);
}
/*************************** IS LOWER **********************************/
static int _is_lower_condition(obin_string data, obin_mem_t index) {
	return islower(data[index]);
}

ObinAny obin_string_is_lower(ObinState* state, ObinAny self) {
	if(!obin_any_is_string(self)) {
		return obin_raise_type_error(state, "obin_string_is_lower call from other type", self);
	}
	return _check_condition(state, self, &_is_lower_condition);
}
/*************************** IS UPPER **********************************/
static int _is_upper_condition(obin_string data, obin_mem_t index) {
	return isupper(data[index]);
}

ObinAny obin_string_is_upper(ObinState* state, ObinAny self) {
	if(!obin_any_is_string(self)) {
		return obin_raise_type_error(state, "obin_string_is_upper call from other type", self);
	}
	return _check_condition(state, self, &_is_upper_condition);
}
/*************************** IS SPACE **********************************/
static int _is_space_condition(obin_string data, obin_mem_t index) {
	return isspace(data[index]);
}

ObinAny obin_string_is_space(ObinState* state, ObinAny self) {
	if(!obin_any_is_string(self)) {
		return obin_raise_type_error(state, "obin_string_is_space call from other type", self);
	}
	return _check_condition(state, self, &_is_space_condition);
}
/************************* SEARCH ***************************************/
typedef ObinAny (*_string_finder)(ObinAny haystack, ObinAny needle,
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
		if (obin_any_number(start) < 0
				|| obin_any_number(start) > haystack_size) {
			obin_raise_invalid_argument(state,
					"String search error -> Invalid start index for search",
					start);
		}

		pstart = (obin_mem_t) obin_any_number(start);
	}

	if (obin_any_is_nil(end)) {
		pend = haystack_size;
	} else {
		if (obin_any_number(end) < 0 || obin_any_number(end) > haystack_size
				|| obin_any_number(end) < pstart) {
			obin_raise_invalid_argument(state,
					"String search error -> Invalid end index for search", end);
		}

		pend = (obin_mem_t) obin_any_number(end);
	}

	if ((pend - pstart) > _string_size(needle)) {
		obin_raise_invalid_slice(state,
				"String search error -> Invalid search range",
				obin_integer_new(pstart), obin_integer_new(pend));
	}

	return finder(_string_data(haystack), _string_data(needle), start, end);
}
/* ****************************** INDEXOF *************************************************************/
ObinAny _string_finder_left(ObinAny haystack, ObinAny needle,
										obin_mem_t start, obin_mem_t end) {

	obin_mem_t size_h;
	obin_mem_t size_n;
	obin_mem_t i;
	obin_mem_t hi;
	obin_mem_t ni;
	obin_char* data_h;
    obin_char* data_n;

    data_h = _string_data(haystack);
    data_n = _string_data(needle);
    size_h = _string_size(haystack);
    size_n = _string_size(needle);

	for (i = start; i < end; i++) {
		// Is the needle at this point in the haystack?
		hi = i;
		ni = 0;
		while(ni < size_n && hi < size_h
				&& (data_h[hi]==data_n[ni]) ){
			ni++;
			hi++;
		}
		if (ni == size_n) {
			// Found match!
			return obin_integer_new(i);
		}
		// Didn't match here.  Try again further along haystack.
	}

	return obin_integer_new(STRING_INDEX_NOT_FOUND);
}

ObinAny obin_string_index_of(ObinState* state, ObinAny self, ObinAny other,
		ObinAny start, ObinAny end) {

	if(!obin_any_is_string(self)) {
		return obin_raise_type_error(state, "obin_string_indexof call from other type", self);
	}

	if(!obin_any_is_string(other)) {
		return obin_raise_type_error(state, "String.indexof invalid argument type", other);
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
ObinAny _string_finder_right(ObinAny haystack, ObinAny needle,
obin_mem_t start, obin_mem_t end) {
	obin_mem_t size_h;
	obin_mem_t size_n;
	obin_mem_t i;
	obin_mem_t hi;
	obin_mem_t ni;
	obin_char* data_h;
    obin_char* data_n;

    data_h = _string_data(haystack);
    data_n = _string_data(needle);
    size_h = _string_size(haystack);
    size_n = _string_size(needle);

	for (i = end - 1; i <= start; i--) {
		/*for is to creepy in that case, while is more readable */
		hi = i;
		ni = size_n - 1;
		while (hi > 0 && ni > 0 && (data_h[hi] == data_n[ni])) {
				--hi;
				--ni;
		}

		if (ni == 0) {
			// Found match!
			return obin_integer_new(i - size_n - 1);
		}
		// Didn't match here.  Try again further along haystack.
	}

	return obin_integer_new(STRING_INDEX_NOT_FOUND);
}

ObinAny obin_string_last_index_of(ObinState* state, ObinAny self, ObinAny other,
		ObinAny start, ObinAny end) {

	if(!obin_any_is_string(self)) {
		return obin_raise_type_error(state, "obin_string_last_indexof call from other type", self);
	}

	if(!obin_any_is_string(other)) {
		return obin_raise_type_error(state, "String.last_indexof invalid argument type", other);
	}

	return _obin_string_find(state, self, other, start, end,
			&_string_finder_right);
}

ObinAny obin_string_at(ObinState* state, ObinAny self, ObinAny index){
	if(!obin_any_is_string(self)) {
		return obin_raise_type_error(state, "obin_string_last_indexof call from other type", self);
	}
}
/*
 /********************** BUILDERS ******************************************/
/* TODO IMPLEMENT
 ObinAny obin_string_format(ObinState* state, ObinAny format, ...);*/

ObinAny obin_string_dublicate(ObinState* state, ObinAny self, ObinAny _count) {
	obin_mem_t size;
	obin_mem_t count;
	obin_char* data;

	if(!obin_any_is_string(self)) {
		return obin_raise_type_error(state, "obin_string_dublicate call from other type", self);
	}

	if(obin_string_is_empty(state, self)) {
		return self;
	}

	if (obin_any_is_nil(_count)) {
		count = 1;
	} else {
		if(!obin_any_is_integer(_count)) {
			return obin_raise_type_error(state, "String.dublicate count must be integer", self);
		}

		obin_assert(obin_any_is_integer(_count));
		count = obin_any_integer(_count);
	}

	size = _string_size(self) * count;
	data = obin_malloc_collection(state, obin_char, size + 1);

	for (; count > 0; count--, data += _string_size(self)) {
		obin_memcpy(data, _string_data(self), _string_size(self));
	}

	return obin_string_new_char_array(state, data, size, OTRUE);
}

ObinAny obin_string_split(ObinState* state, ObinAny self, ObinAny separator) {
	ObinAny result;

	obin_mem_t current;
	obin_mem_t previous;

	if(!obin_any_is_string(self)) {
		return obin_raise_type_error(state, "obin_string_split call from other type", self);
	}
	if(!obin_any_is_string(separator)) {
		return obin_raise_type_error(state, "String.split invalid argument type, String expected", self);
	}

	result = obin_array_new(state, OBIN_SPLIT_STRING_DEFAULT_ARRAY_SIZE);

	if (_string_size(separator) > _string_size(self)) {
		/*can`t split */
		return result;
	}

	current = 0;
	previous = 0;

	while (OTRUE) {
		current = obin_any_integer(
				_string_finder_left(self, separator, previous, _string_size(self))
				);

		if (current == STRING_INDEX_NOT_FOUND) {
			return result;
		}
		if (current == 0) {
			previous = current + _string_size(separator);
			continue;
		}

		obin_array_add(state, result,
				obin_string_new_char_array(state, _string_data(self) + previous,
						current - previous));

		previous = current + _string_size(separator);
	}

	return result;
}

ObinAny obin_string_concat(ObinState* state, ObinAny str1, ObinAny str2) {
	obin_char* data;
	obin_mem_t size;

	if(!obin_any_is_string(str1)) {
		return obin_raise_type_error(state, "obin_string_concat call from other type", str1);
	}
	if(!obin_any_is_string(str2)) {
		return obin_raise_type_error(state, "String.concat invalid argument type, String expected", str2);
	}

	if (_string_size(str1) == 0) {
		return obin_string_from_string(str2);
	}
	if (_string_size(str2) == 0) {
		return obin_string_from_string(str1);
	}

	size = _string_size(str1) + _string_size(str2);

	if (size == 0) {
		return obin_string_empty();
	}

	if (size == 1) {
		return obin_char_new(
				_string_size(str1) == 0 ?
						_string_data(str2)[0] : _string_data(str1)[0]);
	}

	data = obin_malloc_collection(state, obin_char, size);

	obin_memcpy(data, _string_data(str1), _string_size(str1));
	obin_memcpy(data + _string_size(str1), _string_data(str2),
			_string_size(str2));

	return _obin_string_new_char_array(state, data, size, OTRUE);
}

ObinAny obin_string_join(ObinState* state, ObinAny self, ObinAny collection) {
	ObinAny iterator;
	ObinAny value;
	ObinAny result;

	if(!obin_any_is_string(self)) {
		return obin_raise_type_error(state, "obin_string_join call from other type", self);
	}

	result = obin_ctx_get()->internal_strings.Empty;
	iterator = obin_iterator(state, collection);

	while (OTRUE) {
		value = obin_next(state, iterator);
		if (obin_is_stop_iteration(value)) {
			obin_destroy(iterator);
			return result;
		}

		result = obin_string_concat(result, value);
		result = obin_string_concat(result, self);
	}

	return result;
}

/* //native
 str.startswith(prefix[, start[, end]])
 str.lstrip([chars])
 str.rstrip([chars])
 str.splitlines([keepends])
 */
