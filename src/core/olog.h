#ifndef OBIN_OLOG_H_
#define OBIN_OLOG_H_

#ifdef NDEBUG
#define OLOGDEBUG(message)
#define OLOGINFO(message)
#define OLOGERROR(message)
#else
#define OLOGDEBUG(message)
#define OLOGINFO(message)
#define OLOGERROR(message)

typedef enum{
	EOBIN_LOGLEVEL_DEBUG,
	EOBIN_LOGLEVEL_INFO,
	EOBIN_LOGLEVEL_ERROR,
} LogLevel;

void _log(ObinState* state, LogLevel level, ObinAny message, ...);

#endif



#endif /* OLOG_H_ */
