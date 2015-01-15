#ifndef OBIN_OTYPES_H_
#define OBIN_OTYPES_H_

#include <limits.h>
#include <stddef.h>
#include <stdint.h>

#ifndef INT32_MAX
# define INT32_MAX (0x7fffffffL)
#endif
#ifndef INT32_MIN
# define INT32_MIN INT32_C(0x80000000)
#endif
#ifndef UINT8_MAX
# define UINT8_MAX 0xff
#endif

#ifndef UINT32_MAX
# define UINT32_MAX (0xffffffffUL)
#endif

#endif
