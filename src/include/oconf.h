#ifndef OCONF_H
#define OCONF_H

#include <stdarg.h>
#include <limits.h>
#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <ctype.h>

#define OFALSE 0
#define OTRUE 1
#define ONULL NULL

#ifndef ODEBUG
#ifndef NDEBUG
#define ODEBUG 1
#endif
#endif

/*#define OBIN_MEMORY_DEBUG 1*/


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
#define obin_index	obin_mem_t
#define OBIN_MEM_MAX SIZE_MAX

#define obin_int8_t int8_t
#define obin_int32_t int32_t
#define obin_uint32_t uint32_t

typedef obin_int8_t obin_bool;
typedef double obin_float;
typedef void* obin_pointer;
typedef FILE* obin_file;

typedef long obin_integer;
typedef const char* obin_string;
typedef char obin_char;
typedef unsigned char obin_byte;

/* Needed for convertion between numbers and strings */
#define OBIN_INTEGER_FORMATTER "%ld"
#define OBIN_POINTER_FORMATTER "%p"
#define OBIN_FLOAT_FORMATTER "%f"

/* DIRECTORY_SEPARATOR */
#if defined(_WIN32)
#define OBIN_DIR_SEPARATOR	"\\"
#else
#define OBIN_DIR_SEPARATOR	"/"
#endif
#define OBIN_PRINT_SEPARATOR '\44'
#define OBIN_COUNT_TAB_SPACES 4

#define OBIN_DEFAULT_ARRAY_SIZE 10
#define OBIN_DEFAULT_TABLE_SIZE 4
#define OBIN_TABLE_LOAD_FACTOR 0.8

/*TODO replace it with bytes */
#define OBIN_DEFAULT_HEAP_SIZE 1024 * 1024
#define OBIN_MAX_HEAP_SIZE 1024 * 1024 * 100

#define OBIN_MAX_CAPACITY OBIN_MEM_MAX - 1
/*TODO rename to OBIN_INDEX_NOT_FOUND */
#define OBIN_INVALID_INDEX -1

/*
@@ OBINI_MAXSTACK limits the size of the stack.
** CHANGE it if you need a different limit. This limit is arbitrary;
** its only purpose is to stop Obin to consume unlimited stack
** space (and to reserve some numbers for pseudo-indices).
*/
#define OBIN_STACK_MAX_SIZE  (INT_MAX / 2)

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


#ifdef __GNUC__
#define OBIN_STMT_START  ({
#define OBIN_STMT_END    })
#else
#define OBIN_STMT_START  do {
#define OBIN_STMT_END    } while (0)
#endif

#ifndef ODEBUG
#define obin_abort() abort()
#else
#define obin_abort()						\
OBIN_STMT_START						        	\
fprintf (stderr, "Panic in %s:%i: %s \n",			\
	 __FILE__, __LINE__, __FUNCTION__);				\
abort ();								\
OBIN_STMT_END
#endif

#define obin_panic(message)      \
OBIN_STMT_START						        	\
fprintf (stderr, "Panic %s:%i: %s: message:%s\n",			\
	 __FILE__, __LINE__, __FUNCTION__, message);				\
exit(-1);								\
OBIN_STMT_END

#ifndef ODEBUG
#define obin_assert assert
#else
#define obin_assert(condition)						\
OBIN_STMT_START						         	\
if (!(condition)) {						       	\
    fprintf (stderr, "%s:%i: %s: assertion `" #condition "' failed\n",	\
	     __FILE__, __LINE__, __FUNCTION__);				\
    abort();								\
 }									\
OBIN_STMT_END
#endif

/*************ALIASES******/
#define obin_vfprintf vfprintf
#define obin_sprintf sprintf
#define obin_snprintf snprintf
#define obin_vprintf vprintf

#define obin_strlen strlen
#define obin_strstr strstr
#define obin_strncmp strncmp

#define obin_memcpy memcpy
#define obin_memmove memmove
#define obin_strcpy strcpy
#define obin_memset memset

/**********LOG***********/
#define OBIN_LOG_ENABLE
#ifdef OBIN_LOG_ENABLE
/* LOG_LEVELS
 * you can use such values for level verbosity
 * 3 = RAW
 * 2 = INFO
 * 1 = WARNING
 * 0 = ERROR
 * each module which want to log messages send verbosity to log function
 * log occured only if verbosity <= OBIN_LOG_##MODULENAME
 * using of log function are not permitted in header files
 *  */
#define OBIN_LOG_MEMORY 2
#define OBIN_LOG_COMMON 2
#endif

/*************STRING*********/
#define OBIN_STRING_NOT_FOUND -1


#endif
