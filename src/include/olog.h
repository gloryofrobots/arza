#ifndef OBIN_OLOG_H_
#define OBIN_OLOG_H_
#include "obuiltin.h"



/*void _panic(ObinState* state, obin_string format, ...) {
	va_list myargs;
	va_start(myargs, format);
	obin_vfprintf(stderr, format, myargs);
	va_end(myargs);
	obin_abort();
}*/
#ifdef OBIN_LOG_ENABLE
#define OBIN_MODULE_LOG(module_name)\
/* YOU MUST DEFINE OBIN_##module_name##LOG_LEVEL in oconf.h*/ \
static obin_integer _RAW = 3; \
static obin_integer _INFO = 2; \
static obin_integer _WARN = 1; \
static obin_integer _ERR = 0; \
static obin_integer _ALL = -1; \
static void _log(ObinState* state, obin_integer verbosity, obin_string format, ...) { \
	if(OBIN_LOG_##module_name < verbosity) { \
		return; \
	} \
	va_list myargs; \
	va_start(myargs, format); \
	obin_log(state, format, myargs); \
	va_end(myargs); \
}
#else
#define OBIN_MODULE_LOG(module_name)\
static obin_integer _INFO = 2; \
static obin_integer _WARN = 1; \
static obin_integer _ERR = 0; \
static obin_integer _ALL = -1; \
static void _log(ObinState* state, obin_integer verbosity, obin_string format, ...) { }
#endif

void obin_log(ObinState* state, obin_string message, ...);


#endif /* OLOG_H_ */
