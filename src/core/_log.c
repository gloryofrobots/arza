#include <obin.h>

void olog(OState* state, ostring format, ...) {
	va_list myargs;
	va_start(myargs, format);
	ovfprintf(stdout, format, myargs);
	va_end(myargs);
}
