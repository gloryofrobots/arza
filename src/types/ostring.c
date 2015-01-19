#include "../ointernal.h"
#include <ocontext.h>
#include <stdarg.h>

/* ALIASES */
#define _strlen strlen
#define _strstr strstr
#define _snprintf snprintf

/* SIZE FOR BUFFER IN STACK USED TO WRITE INTS AND FLOATS TO STRING */

#define _TEMP_BUFFER_SIZE 256

typedef struct {
	OBIN_CELL_HEADER;
	obin_integer hash;
	obin_mem_t capacity;
	/* we have array here to store both single chars and pointers to malloced data */
	obin_mem_t size;
	obin_char data[1];
} ObinString;

#define _string(any) ((ObinString*) obin_any_cell(any))
#define _string_data(any) (_string(any)->data)
#define _string_size(any) (_string(any)->size)
#define _string_capacity(any) (_string(any)->capacity)

#define CHECK_STRING_TYPE(string) \
	OBIN_ANY_CHECK_TYPE(string, EOBIN_TYPE_STRING)

#define IS_CHARACTER(any) (_string_size(any) == 1)

/********************************** TYPE TRAIT ***********************************************/

static ObinAny method__string__(ObinState* state, ObinAny self) {
	return  self;
}

static ObinAny method__destroy__(ObinState* state, ObinAny self) {
	ObinString * str;
	CHECK_STRING_TYPE(self);
	if(!IS_CHARACTER(self)) {
		obin_free(_string_data(self));
	}

	obin_free(obin_any_cell(self));
	return ObinNothing;
}

static ObinAny method__iterator__(ObinState* state, ObinAny self) {

	return ObinNothing;
}

static struct ObinTypeTrait ObinStringTypeTrait = {
		method__string__,
		method__destroy__,
		obin_string_clone,
		method__iterator__,
		0 /* __next__ */
};

/* constructors */
ObinAny obin_string_new(ObinState* state, obin_string data) {
	int len;

	len = _strlen(data);
	if (len == 0) {
		return obin_string_new_char_array(state, 0, 0);
	}

	return obin_string_new_char_array(state, data, len);
}

ObinAny obin_string_new_char(ObinState* state, obin_char ch) {
	obin_char temp[1];
	temp[0] = ch;
	return obin_string_new_char_array(state, temp, 1);
}

ObinAny _obin_string_new_char_array(ObinState* state, obin_char* data,
obin_mem_t size, int is_shared) {
	ObinString* self;

	self = obin_malloc_type(state, ObinString);
	self->type_trait = &ObinStringTypeTrait;
	/*empty string*/
	if(size == 0) {
		self->capacity = 1;
		self->size = 0;
		self->data[0] = '\0';
	} else if (size == 1) {
		/*we be char now */
		self->capacity = size;
		self->size = size;
		self->data[0] = data[0];
	} else {
		self->capacity = size + 1;
		self->size = size;
		if(is_shared == 1) {
			self->data = obin_malloc_collection(state, obin_char, self->capacity);
			obin_memcpy(self->data, data, size);
		}
		else{
			self->data = data;
		}
		self->data[self.size] = '\0';
	}

	return obin_cell_new(EOBIN_TYPE_STRING, self);
}

/*@param data array without \0
 *@param size array size
 */
ObinAny obin_string_new_char_array(ObinState* state, obin_char* data,
obin_mem_t size) {
	return _obin_string_new_char_array(state, data, size, OFALSE);
}

ObinAny obin_string_clone(ObinState* state, ObinAny string) {
	ObinString * source;

	CHECK_STRING_TYPE(string);

	source = obin_any_cast_cell(source, ObinString);

	/* bitwise copy is good for 1-size strings */
	if (IS_CHARACTER(source)) {
		return string;
	}

	return obin_string_new_char_array(state, source->data, source->size);
}

/* ******************** ATTRIBUTES ***********************************************/
ObinAny obin_string_length(ObinState* state, ObinAny self) {
	CHECK_STRING_TYPE(self);
	return obin_integer_new(_string_size(self));
}

/******************************** MODIFICATIONS *************************************/
/*  function for modify char arrays , return 0 for stop iteration */
typedef int (*_string_modifier)(obin_string data, obin_mem_t index);

/* clone string and modify it`s content by modifier */
ObinAny _clone_and_modify(ObinState* state, ObinAny self,
		_string_modifier modify) {
	ObinAny clone;
	obin_mem_t i;

	CHECK_STRING_TYPE(self);

	clone = obin_string_from_string(self);

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
	return _clone_and_modify(state, self, modifier);
}
/********************* UPPERCASE *************************/
static int _uppercase_modify(obin_string data, obin_mem_t index) {
	data[index] = toupper(data[index]);
	return OTRUE;
}

ObinAny obin_string_to_uppercase(ObinState* state, ObinAny self) {
	static _string_modifier modifier = _uppercase_modify;
	return _clone_and_modify(state, self, modifier);
}

/********************* LOWERCASE ***************************/
static int _lowercase_modify(obin_string data, obin_mem_t index) {
	data[index] = tolower(data[index]);
	return OTRUE;
}

ObinAny obin_string_to_lowercase(ObinState* state, ObinAny self) {
	static _string_modifier modifier = _lowercase_modify;
	return _clone_and_modify(state, self, modifier);
}

/************** CONDITIONS **************************************/
/*  function for checking string content by some condition*/
typedef int (*_string_condition)(obin_string data, obin_mem_t index);

/* check string content for condition */
ObinAny _check_condition(ObinState* state, ObinAny self,
		_string_condition condition) {
	obin_mem_t i;

	CHECK_STRING_TYPE(self);


	for (i = 0; i < _string_size(self); i++) {
		if (condition(_string_data(self), i) == 0) {
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
	return _check_condition(state, self, &_is_alphanum_condition);
}

/*************************** ISALPHA **********************************/
static int _is_alpha_condition(obin_string data, obin_mem_t index) {
	return isalpha(data[index]);
}

ObinAny obin_string_is_alpha(ObinState* state, ObinAny self) {
	return _check_condition(state, self, &_is_alpha_condition);
}

/*************************** ISDIGIT **********************************/
static int _is_digit_condition(obin_string data, obin_mem_t index) {
	return isdigit(data[index]);
}

ObinAny obin_string_is_digit(ObinState* state, ObinAny self) {
	return _check_condition(state, self, &_is_digit_condition);
}
/*************************** IS LOWER **********************************/
static int _is_lower_condition(obin_string data, obin_mem_t index) {
	return islower(data[index]);
}

ObinAny obin_string_is_lower(ObinState* state, ObinAny self) {
	return _check_condition(state, self, &_is_lower_condition);
}
/*************************** IS UPPER **********************************/
static int _is_upper_condition(obin_string data, obin_mem_t index) {
	return isupper(data[index]);
}

ObinAny obin_string_is_upper(ObinState* state, ObinAny self) {
	return _check_condition(state, self, &_is_upper_condition);
}
/*************************** IS SPACE **********************************/
static int _is_space_condition(obin_string data, obin_mem_t index) {
	return isspace(data[index]);
}

ObinAny obin_string_is_space(ObinState* state, ObinAny self) {
	return _check_condition(state, self, &_is_space_condition);
}
/************************* SEARCH ***************************************/
typedef ObinAny (*_string_finder)(ObinString* haystack, ObinString* needle,
obin_mem_t start, obin_mem_t end);

ObinAny _obin_string_find(ObinState* state, ObinAny self, ObinAny other,
		ObinAny start, ObinAny end, _string_finder finder) {
	ObinString* haystack;
	ObinString* needle;
	obin_mem_t pstart;
	obin_mem_t pend;

	CHECK_STRING_TYPE(self);
	CHECK_STRING_TYPE(other);

	haystack = (ObinString*) obin_any_cell(self);
	needle = (ObinString*) obin_any_cell(other);

	if (obin_any_is_nil(start)) {
		pstart = 0;
	} else {
		if (obin_any_number(start) < 0
				|| obin_any_number(start) > haystack->size) {
			obin_raise_invalid_argument(state,
					"String search error -> Invalid start index for search",
					start);
		}

		pstart = (obin_mem_t) obin_any_number(start);
	}

	if (obin_any_is_nil(end)) {
		pend = haystack->size;
	} else {
		if (obin_any_number(end) < 0 || obin_any_number(end) > haystack->size
				|| obin_any_number(end) < pstart) {
			obin_raise_invalid_argument(state,
					"String search error -> Invalid end index for search", end);
		}

		pend = (obin_mem_t) obin_any_number(end);
	}

	if ((pend - pstart) > needle->size) {
		obin_raise_invalid_slice(state,
				"String search error -> Invalid search range",
				obin_integer_new(pstart), obin_integer_new(pend));
	}

	return finder(haystack, needle, start, end);
}
#define STRING_INDEX_NOT_FOUND -1
/* ****************************** INDEXOF *************************************************************/
ObinAny _string_finder_left(ObinString* haystack, ObinString* needle,
obin_mem_t start, obin_mem_t end) {

	obin_mem_t i;
	obin_char *h;
	obin_char *n;

	for (i = start; i < end; i++) {
		// Is the needle at this point in the haystack?
		for (h = haystack->data[i], n = needle->data; *h && *n && (*h == *n);
				++h, ++n) {
			// Match is progressing
		}
		if (*n == '\0') {
			// Found match!
			return obin_integer_new(i);
		}
		// Didn't match here.  Try again further along haystack.
	}

	return obin_integer_new(STRING_INDEX_NOT_FOUND);
}

ObinAny obin_string_index_of(ObinState* state, ObinAny self, ObinAny other,
		ObinAny start, ObinAny end) {
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
ObinAny _string_finder_right(ObinString* haystack, ObinString* needle,
obin_mem_t start, obin_mem_t end) {
	obin_mem_t i;
	obin_mem_t hi;
	obin_mem_t ni;
	obin_char *h;
	obin_char *n;

	for (i = end - 1; i <= start; i--) {
		/*for is to creepy in that case, while is more readable */
		hi = i;
		ni = needle->size - 1;
		while (1) {
			if (hi > 0 && ni > 0 && (haystack->data[hi] == needle->data[ni])) {
				--hi;
				--ni;
			} else {
				break;
			}
		}
		if (ni == 0) {
			// Found match!
			return obin_integer_new(i - needle->size - 1);
		}
		// Didn't match here.  Try again further along haystack.
	}

	return obin_integer_new(STRING_INDEX_NOT_FOUND);
}

ObinAny obin_string_last_index_of(ObinState* state, ObinAny self, ObinAny other,
		ObinAny start, ObinAny end) {
	return _obin_string_find(state, self, other, start, end,
			&_string_finder_right);
}
/*
 /********************** BUILDERS ******************************************/
/* TODO IMPLEMENT
 ObinAny obin_string_format(ObinState* state, ObinAny format, ...);*/

ObinAny obin_string_dublicate(ObinState* state, ObinAny self, ObinAny _count) {
	obin_mem_t size;
	obin_mem_t count;
	ObinString* str;
	obin_char* data;

	CHECK_STRING_TYPE(self);

	str = (ObinString*) obin_any_cell(self);
	if (obin_any_is_nil(_count)) {
		count = 0;
	} else {
		obin_assert(obin_any_is_integer(_count));
		count = obin_any_integer(_count);
	}

	size = str->size * count;
	data = obin_malloc_collection(state, obin_char, size + 1);

	for (; count > 0; count--, data += str->size) {
		obin_memcpy(data, str->data, str->size);
	}

	return obin_string_new_char_array(state, data, size, OTRUE);
}

static ObinAny _obin_cell_to_string(ObinState* state, ObinAny any) {
	obin_assert(obin_any_is_cell(any));
    return obin_type_call(any, __string__);
}

/* TODO make chars and strings the same i think */
ObinAny obin_any_to_string(ObinState* state, ObinAny any) {
	char temp[_TEMP_BUFFER_SIZE] = '\0';
	ObinContext* ctx;

	ctx = obin_ctx_get();

	switch (any.type) {
	case EOBIN_TYPE_STRING:
		return any;
		break;
	case EOBIN_TYPE_INTEGER:
		_snprintf(temp, _TEMP_BUFFER_SIZE, OBIN_INTEGER_FORMATTER,
				obin_any_integer(any));
		return obin_string_new(state, temp);
		break;
	case EOBIN_TYPE_FLOAT:
		_snprintf(temp, _TEMP_BUFFER_SIZE, OBIN_FLOAT_FORMATTER,
				obin_any_float(any));
		return obin_string_new(state, temp);
		break;
	case EOBIN_TYPE_TRUE:
		return ctx->internal_strings.True;
		break;
	case EOBIN_TYPE_FALSE:
		return ctx->internal_strings.False;
		break;
	case EOBIN_TYPE_NIL:
		return ctx->internal_strings.Nil;
		break;
	case EOBIN_TYPE_NOTHING:
		return ctx->internal_strings.Nothing;
		break;

	case EOBIN_TYPE_BIG_INTEGER:
	case EOBIN_TYPE_ARRAY:
	case EOBIN_TYPE_DICT:
	case EOBIN_TYPE_TUPLE:
	case EOBIN_TYPE_COMPOSITE_CELL:
		return _obin_cell_to_string(state, any);
		break;
	default:
		obin_raise_invalid_argument(state,
				"Any to string convertion error -> unprintable internal type",
				obin_integer_new(any.type));
	}
}

#define OBIN_SPLIT_STRING_DEFAULT_ARRAY_SIZE 8

ObinAny obin_string_split(ObinState* state, ObinAny self, ObinAny separator) {
	ObinAny result;

	obin_mem_t current;
	obin_mem_t previous;

	CHECK_STRING_TYPE(self);
	CHECK_STRING_TYPE(separator);

	result = obin_array_new(state, OBIN_SPLIT_STRING_DEFAULT_ARRAY_SIZE);

	if (_string_size(separator) > _string_size(self)) {
		/*can`t split */
		return result;
	}

	current = 0;
	previous = 0;

	while (1) {
		current = obin_any_integer(
						_string_finder_left(_string_data(self),
								_string_data(separator),
								previous,
								_string_size(self)));

		if (current == STRING_INDEX_NOT_FOUND) {
			return result;
		}
		if (current == 0) {
			previous = current + _string_size(separator);
			continue;
		}

		obin_array_add(state, result,
				obin_string_new_char_array(state, _string_data(self) + previous, current - previous));

		previous = current + _string_size(separator);
	}

	return result;
}

ObinAny _obin_string_concat(ObinState* state, ObinAny str1, ObinAny str2) {
	obin_char* data;
	obin_mem_t size;

	OBIN_CHECK_STRING_TYPE(str1);
	OBIN_CHECK_STRING_TYPE(str2);

	if(_string_size(str1) == 0){
		return obin_string_from_string(str2);
	}
	if(_string_size(str2) == 0){
		return obin_string_from_string(str1);
	}

	size = _string_size(str1) + _string_size(str2);

	if(size == 0) {
		return obin_ctx_get()->internal_strings.Empty;
	}

	if(size == 1) {
		return obin_string_new_char(_string_size(str1) == 0
				? _string_data(str2)[0] : _string_data(str1)[0]);
	}

	data = obin_malloc_collection(state, obin_char, size);
	obin_memcpy(data, _string_data(str1), _string_size(str1));
	obin_memcpy(data + _string_size(str1), _string_data(str2), _string_size(str2));

	return _obin_string_new_char_array(state, data, size, OTRUE);
}

ObinAny obin_string_concat(ObinState* state, ObinAny str1, ObinAny str2) {
	OBIN_CHECK_STRING_TYPE(str1);
	return _obin_string_concat(state, str1, obin_any_to_string(str2));
}

ObinAny obin_string_join(ObinState* state, ObinAny self, ObinAny collection) {
	ObinAny iterator;
	ObinAny value;
	ObinAny result;

	CHECK_STRING_TYPE(self);
	/*TODO EMPTY STRINGS WILL CRASH NOW */
	result = obin_ctx_get()->internal_strings.Empty;

	iterator = obin_iterator(state, collection);
	while(1){
		value = obin_next(state, iterator);
		if(obin_any_is_nothing(value)){
			obin_del(iterator);
			return result;
		}

		result = obin_string_concat(result, value);
		result = obin_string_concat(result, self);
	}
}

/*
 //native
 str.startswith(prefix[, start[, end]])
 str.lstrip([chars])
 str.rstrip([chars])
 str.splitlines([keepends])
 */
