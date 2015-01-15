#ifndef OBIN_OCONF_H
#define OBIN_OCONF_H
#include "otypes.h"

//C++ support
#ifdef __cplusplus
# define OBIN_BEGIN_DECLARATIONS  extern "C" {
# define OBIN_END_DECLARATIONS    }
#else
# define OBIN_BEGIN_DECLARATIONS
# define OBIN_END_DECLARATIONS
#endif


//DIRECTORY_SEPARATOR
#if defined(_WIN32)
#define OBIN_DIR_SEPARATOR	"\\"
#else
#define OBIN_DIR_SEPARATOR	"/"
#endif

/*
@@ OBINI_BITSINT defines the number of bits in an int.
** CHANGE here if Lua cannot automatically detect the number of bits of
** your machine. Probably you do not need to change this.
*/
/* avoid overflows in comparison */
#if INT_MAX-20 < 32760		/* { */
#define OBIN_BITSINT	16
#elif INT_MAX > 2147483640L	/* }{ */
/* int has at least 32 bits */
#define OBIN_BITSINT	32
#else				/* }{ */
#error "you must define OBIN_BITSINT with number of bits in an integer"
#endif				/* } */

#define obin_mem_t	size_t
#define OBIN_MEM_MAX SSIZE_MAX

#define obin_int int32_t
#define obin_uint uint32_t

#define obin_double double

typedef void* obin_pointer;
/*
@@ OBINI_MAXSTACK limits the size of the Lua stack.
** CHANGE it if you need a different limit. This limit is arbitrary;
** its only purpose is to stop Lua to consume unlimited stack
** space (and to reserve some numbers for pseudo-indices).
*/
#if OBINI_BITSINT >= 32
#define OBIN_MAXSTACK		1000000
#else
#define OBIN_MAXSTACK		15000
#endif

#define OBIN_DEFAULT_ARRAY_SIZE 10
#define OBIN_DEFAULT_DICT_SIZE 4

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


#endif
