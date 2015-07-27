#include <obin.h>


obool onumber_init(OState* S) {

	return OTRUE;
}

OAny onumber_from_float(ofloat f) {
	return OFloat(f);
}
OAny onumber_from_int(oint i) {
	return OInteger(i);
}

OAny onumber_cast_upper(OState* S, OAny any) {
	switch(OAny_type(any)) {
	case EOBIN_TYPE_INTEGER:
		return OFloat_fromInt(any);
	default:
		 oraise(S, oerrors(S)->TypeError,
		                "onumber_cast_upper already on top", any);
		 return any;
	}
}
