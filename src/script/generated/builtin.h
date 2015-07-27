
/************************* BASE **********************************/

OAny otostring(OState* S, OAny self);

OAny otobool(OState* S, OAny self);

OAny oclone(OState* S, OAny self);

OAny ocompare(OState* S, OAny self, OAny arg1);

OAny ohash(OState* S, OAny self);

/************************* COLLECTION **********************************/

OAny oiterator(OState* S, OAny self);

OAny olength(OState* S, OAny self);

OAny ogetitem(OState* S, OAny self, OAny arg1);

OAny ohasitem(OState* S, OAny self, OAny arg1);

OAny odelitem(OState* S, OAny self, OAny arg1);

OAny osetitem(OState* S, OAny self, OAny arg1, OAny arg2);

/************************* GENERATOR **********************************/

OAny onext(OState* S, OAny self);

/************************* NUMBER **********************************/

OAny otointeger(OState* S, OAny self);

OAny otofloat(OState* S, OAny self);

OAny otonegative(OState* S, OAny self);

OAny oinvert(OState* S, OAny self);

OAny oadd(OState* S, OAny self, OAny arg1);

OAny osubtract(OState* S, OAny self, OAny arg1);

OAny odivide(OState* S, OAny self, OAny arg1);

OAny omultiply(OState* S, OAny self, OAny arg1);

OAny oleftshift(OState* S, OAny self, OAny arg1);

OAny orightshift(OState* S, OAny self, OAny arg1);

OAny omod(OState* S, OAny self, OAny arg1);

OAny obitand(OState* S, OAny self, OAny arg1);

OAny obitor(OState* S, OAny self, OAny arg1);

OAny obitxor(OState* S, OAny self, OAny arg1);
