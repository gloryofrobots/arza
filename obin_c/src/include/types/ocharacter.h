#ifndef OCHARACTER_H_
#define OCHARACTER_H_

obool ocharacter_init(OState* S);

OAny OCharacter(ochar number);
OAny OCharacter_toString(OState* state, OAny self);
OAny OCharacter_toInteger(OAny self);
OAny OCharacter_toFloat(OAny self);

OAny OCharacter_toLower(OState* S, OAny self);
OAny OCharacter_toUpper(OState* S, OAny self);

OAny OCharacter_isAlphanum(OState* S, OAny self);
OAny OCharacter_isAlpha(OState* S, OAny self);
OAny OCharacter_isDigit(OState* S, OAny self);
OAny OCharacter_isLower(OState* S, OAny self);
OAny OCharacter_isUpper(OState* S, OAny self);
OAny OCharacter_isSpace(OState* S, OAny self);
OAny OCharacter_isPunctuation(OState* S, OAny self);

#endif /* OCHAR_H_ */
