#include <obin.h>

void obin_log(ObinState* state, obin_string format, ...) {
	va_list myargs;
	va_start(myargs, format);
	obin_vfprintf(stdout, format, myargs);
	va_end(myargs);
}
