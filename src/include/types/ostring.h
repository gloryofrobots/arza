#ifndef OSTRING_H_
#define OSTRING_H_
#include "obuiltin.h"

obin_bool obin_module_string_init(OState* state);

/* constructors */
OAny obin_string_new(OState* state, obin_string data);
OAny obin_char_new(obin_char ch);

OBehavior* obin_char_behavior();

OAny obin_string_from_carray(OState* state, obin_string data, obin_mem_t size);

OAny obin_string_capitalize(OState* state, OAny self);
OAny obin_string_capitalize_words(OState* state, OAny self);
OAny obin_string_to_lowercase(OState* state, OAny self);
OAny obin_string_to_uppercase(OState* state, OAny self);

OAny obin_string_is_alphanum(OState* state, OAny self);
OAny obin_string_is_alpha(OState* state, OAny self);
OAny obin_string_is_digit(OState* state, OAny self);
OAny obin_string_is_lower(OState* state, OAny self);
OAny obin_string_is_upper(OState* state, OAny self);
OAny obin_string_is_space(OState* state, OAny self);

/*
 Return the lowest index in the string
 where substring sub is found, such that sub is contained
 within s[start:end]. Optional arguments start and end
 are interpreted as in slice notation. Return -1 on failure.
 */
OAny obin_string_index_of(OState* state, OAny self, OAny other,
		OAny start, OAny end);
/*
 Return the highest index in the string
 where substring sub is found, such that sub is contained
 within s[start:end]. Optional arguments start and end
 are interpreted as in slice notation. Return -1 on failure.
 */
OAny obin_string_last_index_of(OState* state, OAny self, OAny other,
		OAny start, OAny end);

OAny obin_string_dublicate(OState* state, OAny self, OAny _count);
OAny obin_string_format(OState* state, OAny format, ...);
OAny obin_string_concat(OState* state, OAny str1, OAny str2);
OAny obin_string_join(OState* state, OAny self, OAny collection);
OAny obin_string_split(OState* state, OAny self, OAny separator);

obin_string obin_string_cstr(OState* state, OAny self);

OAny obin_string_pack(OState* state, obin_index count, ...);

#endif /* OSTRING_H_ */
