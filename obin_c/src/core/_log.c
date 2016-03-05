#include <obin.h>

void olog(OState* S, ostring format, ...) {
	va_list args;
	va_start(args, format);
	ovfprintf(stdout, format, args);
	va_end(args);
}

void ovlog(OState* S, ostring format, va_list args) {
	ovfprintf(stdout, format, args);
	ofprintf(stdout, "\n");
}
