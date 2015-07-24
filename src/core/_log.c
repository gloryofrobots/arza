#include <obin.h>

void obin_log(OState* state, ostring format, ...) {
	va_list myargs;
	va_start(myargs, format);
	ovfprintf(stdout, format, myargs);
	va_end(myargs);
}
