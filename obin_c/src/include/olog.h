#ifndef OBIN_OLOG_H_
#define OBIN_OLOG_H_
#include "obuiltin.h"

#define _INFO 2
#define _WARN 1
#define _ERR 0
#define _ALL -1


/*void _panic(ObinState* S, obin_string format, ...) {
	va_list myargs;
	va_start(myargs, format);
	obin_vfprintf(stderr, format, myargs);
	va_end(myargs);
	obin_abort();
}*/
#ifdef OBIN_LOG_ENABLE
#define OBIN_MODULE_LOG(module_name)\
/* YOU MUST DEFINE OBIN_##module_name##LOG_LEVEL in oconf.h*/ \
static void _log(OState* S, oint verbosity, ostring format, ...) { \
	if(OBIN_LOG_##module_name < verbosity) { \
		return; \
	} \
	va_list myargs; \
	va_start(myargs, format); \
	ovlog(S, format, myargs); \
	va_end(myargs); \
}
#else
#define OBIN_MODULE_LOG(module_name)\
static oint _INFO = 2; \
static oint _WARN = 1; \
static oint _ERR = 0; \
static oint _ALL = -1; \
static void _log(ObinState* S, oint verbosity, ostring format, ...) { }
#endif

void olog(OState* S, ostring message, ...);
void ovlog(OState* S, ostring message, va_list arguments);

#endif /* OLOG_H_ */