#ifndef OSTRING_H_
#define OSTRING_H_
#include <core/obuiltin.h>
/* constructors */
ObinAny obin_string_new(ObinState* state, obin_string data);
ObinAny obin_char_new(ObinState* state, obin_char ch);
ObinAny obin_string_new_char_array(ObinState* state, obin_char* data, obin_mem_t size);

ObinAny obin_string_capitalize(ObinState* state, ObinAny self);
ObinAny obin_string_capitalize_words(ObinState* state, ObinAny self);
ObinAny obin_string_to_lowercase(ObinState* state, ObinAny self);
ObinAny obin_string_to_uppercase(ObinState* state, ObinAny self);

ObinAny obin_string_is_alphanum(ObinState* state, ObinAny self);
ObinAny obin_string_is_alpha(ObinState* state, ObinAny self);
ObinAny obin_string_is_digit(ObinState* state, ObinAny self);
ObinAny obin_string_is_lower(ObinState* state, ObinAny self);
ObinAny obin_string_is_upper(ObinState* state, ObinAny self);
ObinAny obin_string_is_space(ObinState* state, ObinAny self);

/*
 Return the lowest index in the string
 where substring sub is found, such that sub is contained
 within s[start:end]. Optional arguments start and end
 are interpreted as in slice notation. Return -1 on failure.
 */
ObinAny obin_string_index_of(ObinState* state, ObinAny self, ObinAny other,
		ObinAny start, ObinAny end);
/*
 Return the highest index in the string
 where substring sub is found, such that sub is contained
 within s[start:end]. Optional arguments start and end
 are interpreted as in slice notation. Return -1 on failure.
 */
ObinAny obin_string_last_index_of(ObinState* state, ObinAny self, ObinAny other,
		ObinAny start, ObinAny end);

ObinAny obin_string_dublicate(ObinState* state, ObinAny self, ObinAny _count);
ObinAny obin_string_format(ObinState* state, ObinAny format, ...);
ObinAny obin_string_concat(ObinState* state, ObinAny str1, ObinAny str2);
ObinAny obin_string_join(ObinState* state, ObinAny self, ObinAny collection);
ObinAny obin_string_split(ObinState* state, ObinAny self, ObinAny separator);
ObinAny obin_any_to_string(ObinState* state, ObinAny any);

#define OSTR(state, data) obin_string_new(state, data)
#define ONUM(state, num) obin_number_new(state, num)

#endif /* OSTRING_H_ */
