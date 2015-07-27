#ifndef OSTRING_H_
#define OSTRING_H_
#include "obuiltin.h"

obool ostring_init(OState* state);

/* constructors */
OAny OString_new(OState* state, ostring data);
OAny OChar_new(ochar ch);

OAny OString_fromCArray(OState* state, ostring data, omem_t size);

OAny OString_capitalize(OState* state, OAny self);
OAny OString_capitalizeWords(OState* state, OAny self);
OAny OString_toLower(OState* state, OAny self);
OAny OString_toUpper(OState* state, OAny self);

OAny OString_isAlphanum(OState* state, OAny self);
OAny OString_isAlpha(OState* state, OAny self);
OAny OString_isDigit(OState* state, OAny self);
OAny OString_isLower(OState* state, OAny self);
OAny OString_isUpper(OState* state, OAny self);
OAny OString_isSpace(OState* state, OAny self);

/*
 Return the lowest index in the string
 where substring sub is found, such that sub is contained
 within s[start:end]. Optional arguments start and end
 are interpreted as in slice notation. Return -1 on failure.
 */
OAny OString_indexOf(OState* state, OAny self, OAny other,
		OAny start, OAny end);
/*
 Return the highest index in the string
 where substring sub is found, such that sub is contained
 within s[start:end]. Optional arguments start and end
 are interpreted as in slice notation. Return -1 on failure.
 */
OAny OString_lastIndexOf(OState* state, OAny self, OAny other,
		OAny start, OAny end);

OAny OString_dublicate(OState* state, OAny self, OAny _count);
OAny OString_format(OState* state, OAny format, ...);
OAny OString_concat(OState* state, OAny str1, OAny str2);
OAny OString_join(OState* state, OAny self, OAny collection);
OAny OString_split(OState* state, OAny self, OAny separator);

ostring OString_cstr(OState* state, OAny self);

OAny OString_pack(OState* state, oindex_t count, ...);

#endif /* OSTRING_H_ */
