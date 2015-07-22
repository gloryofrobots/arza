#ifndef OSTRING_H_
#define OSTRING_H_
#include "obuiltin.h"

obin_bool obin_module_string_init(ObinState* state);

/* constructors */
ObinAny obin_string_new(ObinState* state, obin_string data);
ObinAny obin_char_new(obin_char ch);

ObinBehavior* obin_char_behavior();

ObinAny obin_string_from_carray(ObinState* state, obin_string data, obin_mem_t size);

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

obin_string obin_string_cstr(ObinState* state, ObinAny self);

ObinAny obin_string_pack(ObinState* state, obin_index count, ...);

#endif /* OSTRING_H_ */
