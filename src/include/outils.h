#ifndef OUTILS_H_
#define OUTILS_H_

#ifndef HAVE_VASPRINTF
int	vasprintf(char **str, const char *fmt, va_list ap);
#endif

#ifndef HAVE_ASPRINTF
int asprintf(char **str, const char *fmt, ...);
#endif


#endif /* OUTILS_H_ */
