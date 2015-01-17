#include "../ointernal.h"

/*
 *
 //native
 str.startswith(prefix[, start[, end]])

 Return True if string starts with the prefix, otherwise return False. prefix can also be a tuple of prefixes to look for. With optional start, test string beginning at that position. With optional end, stop comparing string at that position.

 Changed in version 2.5: Accept tuples as prefix.

 //native
 str.lstrip([chars])

 Return a copy of the string with leading characters removed. The chars argument is a string specifying the set of characters to be removed. If omitted or None, the chars argument defaults to removing whitespace. The chars argument is not a prefix; rather, all combinations of its values are stripped:
 >>>

 >>> '   spacious   '.lstrip()
 'spacious   '
 >>> 'www.example.com'.lstrip('cmowz.')
 'example.com'

 Changed in version 2.2.2: Support for the chars argument.
 //native
 str.rstrip([chars])

 Return a copy of the string with trailing characters removed. The chars argument is a string specifying the set of characters to be removed. If omitted or None, the chars argument defaults to removing whitespace. The chars argument is not a suffix; rather, all combinations of its values are stripped:


 //native
 str.splitlines([keepends])

 Return a list of the lines in the string, breaking at line boundaries. This method uses the universal newlines approach to splitting lines. Line breaks are not included in the resulting list unless keepends is given and true.

 For example, 'ab c\n\nde fg\rkl\r\n'.splitlines() returns ['ab c', '', 'de fg', 'kl'], while the same call with splitlines(True) returns ['ab c\n', '\n', 'de fg\r', 'kl\r\n'].

 Unlike split() when a delimiter string sep is given, this method returns an empty list for the empty string, and a terminal line break does not result in an extra line.
 str.endswith(suffix[, start[, end]])

 Return True if the string ends with the specified suffix, otherwise return False. suffix can also be a tuple of suffixes to look for. With optional start, test beginning at that position. With optional end, stop comparing at that position.

 Changed in version 2.5: Accept tuples as suffix.
 */

typedef struct {
	OBIN_CELL_HEADER;
	OBIN_DEFINE_TYPE_TRAIT(ObinCollectionTrait);

	obin_mem_t size;
	obin_mem_t capacity;

	/* we have array here to store both single chars and pointers to malloced data */
	obin_char data[1];
} ObinString;
#define CHECK_STRING_TYPE(string) \
	OBIN_ANY_CHECK_TYPE(string, EOBIN_TYPE_STRING)

#define IS_CHARACTER(str) (str.capacity == str.size && str.capacity == 1)
#define _strlen strlen

/* constructors */
ObinAny obin_string_new(ObinState* state, obin_string data) {
	int len;

	len = _strlen(data);
	if (len == 0) {
		return obin_raise_error(state, ObinInvalidArgumentError);
	}

	return obin_string_new_from_char_array(state, data, len);
}

ObinAny obin_string_new_from_char_array(ObinState* state, obin_char* data,
obin_mem_t size) {
	ObinString* self;

	self = obin_malloc_type(ObinString);

	self->capacity = size + 1;
	self->size = size;

	/*we be char now */
	if (size == 1) {
		self->data[0] = data[0];
	} else {
		self->data = obin_malloc_collection(obin_char, self->capacity);
		obin_memcpy(self->data, data, size);
	}

	self->data[self.capacity] = '\0';
	return obin_cell_new(EOBIN_TYPE_STRING, self);
}

ObinAny obin_string_new_from_string(ObinState* state, ObinAny string) {
	ObinString * other;

	CHECK_STRING_TYPE(string);

	other = obin_any_cast_cell(other, ObinString);
	return obin_string_new_from_char_array(state, other.data, other->size);
}

/* ******************** ATTRIBUTES ***********************************************/
ObinAny obin_string_length(ObinState* state, ObinAny self) {
	ObinString* str;
	obin_mem_t i;

	CHECK_STRING_TYPE(self);

	str = (ObinString*) obin_any_cell(self);
	return obin_number_new(str->size);
}

/******************************** MODIFICATIONS *************************************/
/*  function for modify char arrays , return 0 for stop iteration */
typedef int (*_string_modifier)(obin_string data, obin_mem_t index);

/* clone string and modify it`s content by modifier */
ObinAny _clone_and_modify(ObinState* state, ObinAny self,
		_string_modifier modify) {
	ObinString* str;
	ObinAny clone;
	obin_mem_t i;

	CHECK_STRING_TYPE(self);

	clone = obin_string_from_string(self);
	str = (ObinString*) obin_any_cell(clone);

	for (i = 0; i < str.size; i++) {
		if (modify(str.data, i) == 0) {
			break;
		}
	}

	return clone;
}

/*********************** CAPITALIZE *************************/
static int _capitalize_modify(obin_string data, obin_mem_t index) {
	if (!isalpha(data[index])) {
		return 1;
	}

	data[index] = toupper(data[index]);
	return 0;
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
	return 1;
}

ObinAny obin_string_capitalize_words(ObinState* state, ObinAny self) {
	static _string_modifier modifier = _capitalize_words_modify;
	return _clone_and_modify(state, self, modifier);
}
/********************* UPPERCASE *************************/
static int _uppercase_modify(obin_string data, obin_mem_t index) {
	data[index] = toupper(data[index]);
	return 1;
}

ObinAny obin_string_to_uppercase(ObinState* state, ObinAny self) {
	static _string_modifier modifier = _uppercase_modify;
	return _clone_and_modify(state, self, modifier);
}

/********************* LOWERCASE ***************************/
static int _lowercase_modify(obin_string data, obin_mem_t index) {
	data[index] = tolower(data[index]);
	return 1;
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
	ObinString* str;
	obin_mem_t i;

	CHECK_STRING_TYPE(self);

	str = (ObinString*) obin_any_cell(self);

	for (i = 0; i < str.size; i++) {
		if (condition(str.data, i) == 0) {
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
#define _strstr strstr
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
			return obin_raise(state, ObinInvalidArgumentError,
					obin_string_new(state, "Invalid start index for search"),
					start);
		}
		pstart = (obin_mem_t) obin_any_number(start);
	}

	if (obin_any_is_nil(end)) {
		pend = haystack->size;
	} else {
		if (obin_any_number(end) < 0 || obin_any_number(end) > haystack->size
				|| obin_any_number(end) < pstart) {
			return obin_raise(state, ObinInvalidArgumentError,
					obin_string_new(state, "Invalid end index for search"), end);
		}
		pend = (obin_mem_t) obin_any_number(end);
	}

	if ((pend - pstart) > needle->size) {
		return obin_raise(state, ObinInvalidArgumentError,
				obin_string_new(state, "Invalid search range"),
				obin_number_new(pstart), obin_number_new(pend));
	}

	return finder(haystack, needle, start, end);
}
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
			return obin_number_new(i);
		}
		// Didn't match here.  Try again further along haystack.
	}

	return obin_number_new(-1);
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
 are interpreted as in slice notation. Return -1 on failure.
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
			return obin_number_new(i - needle->size - 1);
		}
		// Didn't match here.  Try again further along haystack.
	}

	return obin_number_new(-1);
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
	obin_mem_t count;
	ObinString* str;
	ObinString* result;

	CHECK_STRING_TYPE(self);

	str = (ObinString*) obin_any_cell(self);
	count = obin_any_number(_count);

	result = obin_malloc_type(ObinString);
	result->size = str->size * count;
	result->capacity = str->size + 1;
	result->data = obin_malloc_collection(obin_char, result->capacity);

	for (; count > 0; count--, result->data += str->size) {
		obin_memcpy(result->data, str->data, str->size);
	}

	result->data[result->capacity] = '\0';
	return obin_cell_new(EOBIN_TYPE_STRING, result);
}
#define _snprintf snprintf
#define _TEMP_BUFFER_SIZE 256

ObinAny obin_cell_to_string(ObinState* state, ObinAny any){
	ObinCell* cell;

	obin_assert(obin_any_is_cell(any));

	cell = obin_any_cell(any);
}
ObinAny obin_any_to_string(ObinState* state, ObinAny any) {
	char temp[_TEMP_BUFFER_SIZE] = '\0';
	switch(any.type) {
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
		_snprintf(temp, _TEMP_BUFFER_SIZE, OBIN_TRUE_REPR);
		return obin_string_new(state, OBIN_TRUE_REPR);
		break;

	}
	if (obin_any_is_integer(any)) {
	} else if(obin_any_is_float(any)){
	} else if(obin_any_is_float(any)){
		_snprintf(temp, _TEMP_BUFFER_SIZE, OBIN_FLOAT_FORMATTER,
				obin_any_float(any));
		return obin_string_new(state, temp);
	}


	else{
		return obin_cell_to_string(state, any);
	}
}
ObinAny obin_string_concat(ObinState* state, ObinAny first_part, ...);
ObinAny obin_string_join(ObinState* state, ObinAny collection);
ObinAny obin_string_split(ObinState* state, ObinAny self, ObinAny separator);
