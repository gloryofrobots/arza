#ifndef OSTRING_H_
#define OSTRING_H_
#include "obuiltin.h"

obin_bool obin_module_string_init(ObinState* state);

/* constructors */
OAny obin_string_new(ObinState* state, obin_string data);
OAny obin_char_new(obin_char ch);

OBehavior* obin_char_behavior();

OAny obin_string_from_carray(ObinState* state, obin_string data, obin_mem_t size);

OAny obin_string_capitalize(ObinState* state, OAny self);
OAny obin_string_capitalize_words(ObinState* state, OAny self);
OAny obin_string_to_lowercase(ObinState* state, OAny self);
OAny obin_string_to_uppercase(ObinState* state, OAny self);

OAny obin_string_is_alphanum(ObinState* state, OAny self);
OAny obin_string_is_alpha(ObinState* state, OAny self);
OAny obin_string_is_digit(ObinState* state, OAny self);
OAny obin_string_is_lower(ObinState* state, OAny self);
OAny obin_string_is_upper(ObinState* state, OAny self);
OAny obin_string_is_space(ObinState* state, OAny self);

/*
 Return the lowest index in the string
 where substring sub is found, such that sub is contained
 within s[start:end]. Optional arguments start and end
 are interpreted as in slice notation. Return -1 on failure.
 */
OAny obin_string_index_of(ObinState* state, OAny self, OAny other,
		OAny start, OAny end);
/*
 Return the highest index in the string
 where substring sub is found, such that sub is contained
 within s[start:end]. Optional arguments start and end
 are interpreted as in slice notation. Return -1 on failure.
 */
OAny obin_string_last_index_of(ObinState* state, OAny self, OAny other,
		OAny start, OAny end);

OAny obin_string_dublicate(ObinState* state, OAny self, OAny _count);
OAny obin_string_format(ObinState* state, OAny format, ...);
OAny obin_string_concat(ObinState* state, OAny str1, OAny str2);
OAny obin_string_join(ObinState* state, OAny self, OAny collection);
OAny obin_string_split(ObinState* state, OAny self, OAny separator);

obin_string obin_string_cstr(ObinState* state, OAny self);

OAny obin_string_pack(ObinState* state, obin_index count, ...);

#endif /* OSTRING_H_ */
