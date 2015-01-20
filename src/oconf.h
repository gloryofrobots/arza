#ifndef OBIN_OCONF_H
#define OBIN_OCONF_H
#include <limits.h>
#include <stddef.h>
#include <stdint.h>
#include <assert.h>
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

#define obin_mem_t	size_t
#define OBIN_MEM_MAX SSIZE_MAX

#define obin_int32t int32_t
#define obin_uint32t uint32_t

typedef int obin_bool;
typedef double obin_float;
typedef void* obin_pointer;

/* TODO rename to boin_integer */
/*
 * @@ obin_number defines small integer representation in obin, every value which iverflow it will be storen
 * in big number
 */
typedef long obin_integer;
typedef const char* obin_string;
typedef char obin_char;
/* Needed for convertion between numbers and strings */
#define OBIN_INTEGER_FORMATTER "%ld"
#define OBIN_FLOAT_FORMATTER "%f"
/* STOLEN from LUA */
/* C++ support */
#ifdef __cplusplus
# define OBIN_BEGIN_DECLARATIONS  extern "C" {
# define OBIN_END_DECLARATIONS    }
#else
# define OBIN_BEGIN_DECLARATIONS
# define OBIN_END_DECLARATIONS
#endif

/* DIRECTORY_SEPARATOR */
#if defined(_WIN32)
#define OBIN_DIR_SEPARATOR	"\\"
#else
#define OBIN_DIR_SEPARATOR	"/"
#endif

#define OBIN_DEFAULT_ARRAY_SIZE 10
#define OBIN_DEFAULT_DICT_SIZE 4


/*
@@ OBINI_MAXSTACK limits the size of the Lua stack.
** CHANGE it if you need a different limit. This limit is arbitrary;
** its only purpose is to stop Lua to consume unlimited stack
** space (and to reserve some numbers for pseudo-indices).
*/
#define OBIN_STACK_MAX_SIZE  (INT_MAX / 2)


/*
@@ OBIN_API is a mark for all core API functions.
@@ OBINLIB_API is a mark for all auxiliary library functions.
@@ OBINMOD_API is a mark for all standard library opening functions.
** CHANGE them if you need to define those functions in some special way.
** For instance, if you want to create one Windows DLL with the core and
** the libraries, you may want to use the following definition (define
** OBIN_BUILD_AS_DLL to get it).
*/
#if defined(OBIN_BUILD_DLL)	/* { */

#if defined(OBIN_CORE) || defined(OBIN_LIB)	/* { */
#define OBIN_API __declspec(dllexport)
#else						/* }{ */
#define OBIN_API __declspec(dllimport)
#endif						/* } */

#else				/* }{ */

#define OBIN_API		extern

#endif				/* } */

/*
@@ OBINI_FUNC is a mark for all extern functions that are not to be
@* exported to outside modules.
@@ OBINI_DDEF and OBINI_DDEC are marks for all extern (const) variables
@* that are not to be exported to outside modules (OBINI_DDEF for
@* definitions and OBINI_DDEC for declarations).
** CHANGE them if you need to mark them in some special way. Elf/gcc
** (versions 3.2 and later) mark them as "hidden" to optimize access
** when Lua is compiled as a shared library. Not all elf targets support
** this attribute. Unfortunately, gcc does not offer a way to check
** whether the target offers that support, and those without support
** give a warning about it. To avoid these warnings, change to the
** default definition.
*/
#if defined(__GNUC__) && ((__GNUC__*100 + __GNUC_MINOR__) >= 302) && \
    defined(__ELF__)		/* { */
#define OBIN_FUNC	__attribute__((visibility("hidden"))) extern
#define OBIN_DDEC	OBINI_FUNC
#define OBIN_DDEF	/* empty */

#else				/* }{ */
#define OBIN_FUNC	extern
#define OBIN_DDEC	extern
#define OBIN_DDEF	/* empty */
#endif				/* } */

/* END STOLEN from LUA */

#define obin_assert assert
#endif
