#include <stdlib.h>
#include <stdio.h>

#include "../core/oany.h"

#define ST_TAG_SIZE 2

#define BUF_SIZE 33
#define ST_NTH_BIT(n)         (1 << (n))
#define ST_NTH_MASK(n)        (ST_NTH_BIT(n) - 1)
enum
{
    st_tag_mask = ST_NTH_MASK (2)
};
enum {
    ST_SMI_TAG,
    ST_POINTER_TAG,
    ST_CHARACTER_TAG,
    ST_MARK_TAG,
};

static inline int
st_object_tag (uintptr_t object)
{
    return object & st_tag_mask;
}

uintptr_t
st_smi_new (intptr_t num)
{
    return (((uintptr_t) num) << ST_TAG_SIZE) + ST_SMI_TAG;
}

intptr_t
st_smi_value (uintptr_t smi)
{
    return ((intptr_t) smi) >> ST_TAG_SIZE;
}

uintptr_t
st_tag_pointer (void* p)
{
    return ((uintptr_t) p) + ST_POINTER_TAG;
}

void *
st_detag_pointer (uintptr_t oop)
{
    return (void *) (oop - ST_POINTER_TAG);
}
// buffer must have length >= sizeof(int) + 1
// Write to the buffer backwards so that the binary representation
// is in the correct order i.e.  the LSB is on the far right
// instead of the far left of the printed string
char *int2bin(int a, char *buffer, int buf_size) {
	int i = 0;
    buffer += (buf_size - 1);

    for (i = 31; i >= 0; i--) {
        *buffer-- = (a & 1) + '0';

        a >>= 1;
    }

    return buffer;
}

int main() {
    char buffer[BUF_SIZE];
    memset(buffer, 0, BUF_SIZE);
    size_t size = BUF_SIZE - 1;
    int2bin(0xFF000000, buffer, size);

    printf("a = %s\n", buffer);
    printf("l = %ld \n", LONG_MAX);
    printf("i = %ld \n", INT_MAX);
    printf("s = %ld \n", SSIZE_MAX);
    printf("u = %f \n",(float) UINTPTR_MAX);

    printf("l = %ld \n", sizeof(long));
    printf("i = %ld \n", sizeof(int));
    printf("s = %ld \n", sizeof(size_t));
    printf("u = %0.f \n",(float) sizeof(uintptr_t));

    printf("*************************************************\n");

    uintptr_t max = st_tag_pointer((void*) UINTPTR_MAX);
    printf("t = %0.f \n",(float) max);
    uintptr_t restore = st_detag_pointer(max);
    printf("r = %0.f \n",(float) restore);

    memset(buffer, 0, BUF_SIZE);
    int2bin(st_object_tag(max), buffer, size);
    printf("max tag = %s\n", buffer);

    printf("*************************************************\n");
    intptr_t value = 536870911;
//    value = INTPTR_MAX;
    printf("v = %0.f \n",(float) value);
    uintptr_t smi = st_smi_new(value);
    printf("s = %0.f \n",(float) smi);
    intptr_t smi_restore = st_smi_value(smi);
    printf("sr = %0.f \n",(float) smi_restore);


    memset(buffer, 0, BUF_SIZE);
    int2bin(INTPTR_MAX, buffer, size);
    printf("max = %s\n", buffer);

    memset(buffer, 0, BUF_SIZE);
    int2bin((INTPTR_MAX << ST_TAG_SIZE) + ST_SMI_TAG , buffer, size);
    printf(" (INTPTR_MAX << ST_TAG_SIZE) = %s\n", buffer);

    memset(buffer, 0, BUF_SIZE);
    int2bin(536870911, buffer, size);
    printf("536870911 = %s\n", buffer);

    memset(buffer, 0, BUF_SIZE);
    int2bin((536870911 << ST_TAG_SIZE)+ST_SMI_TAG, buffer, size);
    printf("536870911 << ST_TAG_SIZE)+ST_SMI_TAG, = %s\n", buffer);

    uintptr_t check = (536870911 << ST_TAG_SIZE)+ST_POINTER_TAG;
    check = st_tag_pointer(536870911);
    memset(buffer, 0, BUF_SIZE);
    int2bin(st_object_tag(check), buffer, size);
    printf("check = %s\n", buffer);

    memset(buffer, 0, BUF_SIZE);
    int2bin((536870911 << ST_TAG_SIZE)+ST_POINTER_TAG, buffer, size);
    printf("536870911 << ST_TAG_SIZE)+ST_POINTER_TAG, = %s\n", buffer);

    memset(buffer, 0, BUF_SIZE);
    int2bin(536870912, buffer, size);
    printf("536870912 = %s\n", buffer);

    memset(buffer, 0, BUF_SIZE);
    int2bin(max, buffer, size);
    printf("max bits = %s\n", buffer);

    memset(buffer, 0, BUF_SIZE);
    int2bin(st_object_tag(max), buffer, size);
    printf("max tag = %s\n", buffer);

    memset(buffer, 0, BUF_SIZE);
    int2bin(st_object_tag(smi), buffer, size);
    printf("smi tag = %s\n", buffer);

    memset(buffer, 0, BUF_SIZE);
    int2bin(restore, buffer, size);
    printf("restore bits = %s\n", buffer);

}
