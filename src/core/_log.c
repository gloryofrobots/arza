#include <obin.h>

void obin_log(OState* state, ostring format, ...) {
	va_list myargs;
	va_start(myargs, format);
	obin_vfprintf(stdout, format, myargs);
	va_end(myargs);
}
