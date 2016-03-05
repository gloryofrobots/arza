#ifndef __GUARD_OBIN_UTILS_H
#define __GUARD_OBIN_UTILS_H

#ifdef __GNUC__
#define ST_STMT_START  ({
#define ST_STMT_END    })
#else
#define ST_STMT_START  do {
#define ST_STMT_END    } while (0)
#endif

#ifndef ST_DEBUG
#define st_assert(condition) 
#else
#define st_assert(condition)						\
ST_STMT_START						         	\
if (!(condition)) {						       	\
    fprintf (stderr, "%s:%i: %s: assertion `" #condition "' failed\n",	\
	     __FILE__, __LINE__, __FUNCTION__);				\
    abort ();								\
 }									\
ST_STMT_END
#endif

#ifndef ST_DEBUG
#define st_assert_not_reached() 
#else
#define st_assert_not_reached()						\
ST_STMT_START						        	\
fprintf (stderr, "%s:%i: %s: should not reach here\n",			\
	 __FILE__, __LINE__, __FUNCTION__);				\
abort ();								\
ST_STMT_END
#endif
static int fd;
static fpos_t pos;

void switchStdout(const char *newStream)
{
  fflush(stdout);
  fgetpos(stdout, &pos);
  fd = dup(fileno(stdout));
  freopen(newStream, "w", stdout);
}

void revertStdout()
{
  fflush(stdout);
  dup2(fd, fileno(stdout));
  close(fd);
  clearerr(stdout);
  fsetpos(stdout, &pos);
}
void st_log (const char * domain, const char * format, ...);

#endif /* __GUARD_OBIN_UTILS_H_ */
