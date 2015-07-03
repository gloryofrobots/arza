#include <stdlib.h>
#include <stdio.h>
#include "devutils.h"
#include "core/obin.h"



int main() {

	ObinAny f = ObinTrue;

	PRINT_NUMBER(f.type);
	return 0;
}

