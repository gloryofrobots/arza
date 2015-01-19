#include <stdlib.h>
#include <stdio.h>
#include "ointernal.h"

#include "devutils.h"
int xx() { return 2; }


int main() {
	ObinAny num = obin_integer_new(2);
	ObinAny fl = obin_float_new(67.3f);

	PRINT_NUMBER(sizeof(ObinAny));
	ObinAny t = __t();

	PRINT_NUMBER(obin_any_is_true(ObinTrue));
	PRINT_NUMBER(obin_any_is_true(ObinFalse));

	PRINT_NUMBER(obin_any_is_nil(ObinFalse));
	PRINT_NUMBER(obin_any_is_true(t));
	return 0;
}
