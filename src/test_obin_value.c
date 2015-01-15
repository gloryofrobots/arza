#include <stdlib.h>
#include <stdio.h>
#include "otypes.h"
#include "debug_utils.h"

/* immediate values macros */
#define IMMEDIATE(X)      (X==TR_NIL || X==TR_TRUE || X==TR_FALSE || X==TR_UNDEF || TR_IS_FIX(X))
#define IS_FIX(F)         ((F) & 1)
#define FIX2INT(F)        (((int)(F) >> 1))
#define INT2FIX(I)        ((I) << 1 |  1)
#define NIL               ((OBJ)0)
#define FALSE             ((OBJ)2)
#define TRUE              ((OBJ)4)
#define UNDEF             ((OBJ)6)
#define TEST(X)           ((X) == TR_NIL || (X) == TR_FALSE ? 0 : 1)
#define BOOL(X)           ((X) ? TR_TRUE : TR_FALSE)


#define BUF_SIZE 33

int main() {
    char buffer[BUF_SIZE];
    PRINT_NUMBER(sizeof(long));
    PRINT_NUMBER(sizeof(int));
    PRINT_NUMBER(sizeof(double));
    PRINT_NUMBER(sizeof(uintptr_t));
    PRINT_NUMBER(sizeof(intptr_t));

    PRINT_NUMBER(UINTPTR_MAX);
    PRINT_NUMBER(INTPTR_MAX);
    PRINT_NUMBER(LONG_MAX);
    PRINT_NUMBER(SSIZE_MAX);
    PRINT_NUMBER(INT_MAX);


    uintptr_t int2fix_check = INT2FIX(1073741823);
    PRINT_NUMBER((int2fix_check & 1));
    PRINT_NUMBER((1073741823 & 1));

    PRINT_NUMBER(int2fix_check);
    PRINT_BITS(int2fix_check, buffer, BUF_SIZE);

    intptr_t inttfix_restore = FIX2INT(int2fix_check);
    PRINT_NUMBER(inttfix_restore);
    PRINT_BITS(inttfix_restore, buffer, BUF_SIZE);

    PRINT_BITS(INTPTR_MAX, buffer, BUF_SIZE);
    PRINT_BITS(INTPTR_MIN, buffer, BUF_SIZE);

    PRINT_BITS(INTPTR_MAX -1, buffer, BUF_SIZE);
    PRINT_BITS(INTPTR_MIN + 1, buffer, BUF_SIZE);
}
