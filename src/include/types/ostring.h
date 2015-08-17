#ifndef OSTRING_H_
#define OSTRING_H_
#include "obuiltin.h"

obool ostring_init(OState* S);

OAny ostring_concat_collection(OState* S, OAny collection);

/* constructors */
OAny OString(OState* S, ostring data);

OAny OString_fromCArray(OState* S, ostring data, omem_t size);

OAny OString_capitalize(OState* S, OAny self);
OAny OString_capitalizeWords(OState* S, OAny self);
OAny OString_toLower(OState* S, OAny self);
OAny OString_toUpper(OState* S, OAny self);

OAny OString_isAlphanum(OState* S, OAny self);
OAny OString_isAlpha(OState* S, OAny self);
OAny OString_isDigit(OState* S, OAny self);
OAny OString_isLower(OState* S, OAny self);
OAny OString_isUpper(OState* S, OAny self);
OAny OString_isSpace(OState* S, OAny self);

/*
 Return the lowest index in the string
 where substring sub is found, such that sub is contained
 within s[start:end]. Optional arguments start and end
 are interpreted as in slice notation. Return -1 on failure.
 */
OAny OString_indexOf(OState* S, OAny self, OAny other,
		OAny start, OAny end);
/*
 Return the highest index in the string
 where substring sub is found, such that sub is contained
 within s[start:end]. Optional arguments start and end
 are interpreted as in slice notation. Return -1 on failure.
 */
OAny OString_lastIndexOf(OState* S, OAny self, OAny other,
		OAny start, OAny end);

OAny OString_dublicate(OState* S, OAny self, OAny _count);
OAny OString_format(OState* S, OAny format, ...);
OAny OString_concat(OState* S, OAny str1, OAny str2);
OAny OString_join(OState* S, OAny self, OAny collection);
OAny OString_split(OState* S, OAny self, OAny separator);

ostring OString_cstr(OState* S, OAny self);

OAny OString_pack(OState* S, oindex_t count, ...);

#endif /* OSTRING_H_ */
