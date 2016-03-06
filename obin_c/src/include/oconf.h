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
#include <math.h>

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
#ifndef CHAR_MIN
#define CHAR_MIN 0
#endif

#ifndef CHAR_MAX
#define CHAR_MAX 255
#endif

#define OCHAR_MAX UCHAR_MAX

#define omem_t	size_t
#define oindex_t	omem_t
#define OBIN_MEM_MAX SIZE_MAX

#define oint8_t int8_t
#define ouint8_t uint8_t
#define oint32_t int32_t
#define ouint32_t uint32_t

typedef ouint8_t obyte;
typedef obyte obool;
typedef double ofloat;
typedef void* opointer;
typedef FILE* ofile;

typedef long oint;
typedef oint obytecode;

#define OINT_MAX LONG_MAX
#define OINT_MIN LONG_MIN

typedef const char* ostring;
typedef char ochar;
typedef unsigned char ouchar;


/* Needed for convertion between numbers and strings */
#define OBIN_INTEGER_FORMATTER "%ld"
#define OBIN_POINTER_FORMATTER "%p"
#define OBIN_FLOAT_FORMATTER "%g"
#define OBIN_FLOAT_GRANULARITY 10000
/* DIRECTORY_SEPARATOR */
#if defined(_WIN32)
#define OBIN_DIR_SEPARATOR	"\\"
#else
#define OBIN_DIR_SEPARATOR	"/"
#endif
#define OBIN_PRINT_SEPARATOR "\44"
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
#define oabort() abort()
#else
#define oabort()						\
OBIN_STMT_START						        	\
fprintf (stderr, "Panic in %s:%i: %s \n",			\
	 __FILE__, __LINE__, __FUNCTION__);				\
abort ();								\
OBIN_STMT_END
#endif

#define opanic(message)      \
OBIN_STMT_START						        	\
fprintf (stderr, "Panic %s:%i: %s: message:%s\n",			\
	 __FILE__, __LINE__, __FUNCTION__, message);				\
exit(-1);								\
OBIN_STMT_END

#ifndef ODEBUG
#define oassert assert
#else
#define oassert(condition)						\
OBIN_STMT_START						         	\
if (!(condition)) {						       	\
    fprintf (stderr, "%s:%i: %s: assertion `" #condition "' failed\n",	\
	     __FILE__, __LINE__, __FUNCTION__);				\
    abort();								\
 }									\
OBIN_STMT_END
#endif

/*************ALIASES******/
#define __oasprintf asprintf

#define ovfprintf vfprintf
#define ofprintf fprintf
#define osprintf sprintf
#define osnprintf snprintf
#define ovprintf vprintf

#define ostrlen strlen
#define ostrstr strstr
#define ostrncmp strncmp

#define omemcpy memcpy
#define omemmove memmove
#define ostrcpy strcpy
#define omemset memset
#define omalloc malloc
#define ocalloc calloc
#define orealloc realloc
#define ofree free
#define __oabs labs
#define __opow pow
#define __ofmod fmod
#define __oisfinite isfinite
#define __oisinf isinf

#define __otolower tolower
#define __otoupper toupper

#define __oisalpha isalpha
#define __oisdigit isdigit
#define __oisspace isspace
#define __oisupper isupper
#define __oislower islower
#define __oispunct ispunct

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
#define OBIN_LOG_VECTOR 2
#define OBIN_LOG_BYTECODE 2
#endif

/*************STRING*********/
#define OBIN_STRING_NOT_FOUND -1


#endif