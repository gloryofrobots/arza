#ifndef OCOMPILE_H_
#define OCOMPILE_H_

obool oparser_init(OState* S);
OAny OParser_parseString(OState* S, OAny str);
OAny OParser_parseCString(OState* S, ostring str);

#endif /* OCOMPILE_H_ */
