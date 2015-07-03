#ifndef DEBUG_UTILS_H_
#define DEBUG_UTILS_H_

#include <core/obuiltin.h>

ObinAny __t () {
	return ObinTrue;
}
/* buffer must have length >= sizeof(int) + 1
 Write to the buffer backwards so that the binary representation
 is in the correct order i.e.  the LSB is on the far right
 instead of the far left of the printed string
*/
char *int2bin(int a, char *buffer, int buf_size) {
	int i = 0;
    buffer += (buf_size - 1);

    for (i = 31; i >= 0; i--) {
        *buffer-- = (a & 1) + '0';

        a >>= 1;
    }

    return buffer;
}

#define PRINT_BITS(expression, buffer, size) \
    memset(buffer, 0, size); \
    int2bin(expression, buffer, size - 1); \
    printf(#expression " = %s\n", buffer)

#define PRINT_NUMBER(expression) \
    printf(#expression " = %0.f \n", (float)expression)


#endif /* DEBUG_UTILS_H_ */
