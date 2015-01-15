#include <stdlib.h>
#include <stdio.h>
#include "otypes.h"

typedef struct {

} Cell;


typedef struct {
	int8_t type;

	union{
		long number;
		void * cell;
	};
} Any;


int main() {
	printf("size = %d\n", sizeof(Any));
	printf("size double = %d\n", sizeof(double));
	printf("size int32 = %d\n", sizeof(int32_t));
}
