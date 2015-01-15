#ifndef OBIN_OBASE_H_
#define OBIN_OBASE_H_

#include "oconf.h"


typedef uint8_t obin_type;

typedef enum {
	EOBIN_TYPE_INT = 0,
	EOBIN_TYPE_BIG_INT,
	EOBIN_TYPE_DOUBLE,
	EOBIN_TYPE_STRING,
	EOBIN_TYPE_ARRAY,
	EOBIN_TYPE_DICT,
	EOBIN_TYPE_CELL
} EOBIN_TYPE;

typedef enum {
	EOBIN_SUCCESS = 0,
	EOBIN_INTERNAL_ERROR
} EOBIN_RESULT;

#define OBIN_IS_SUCCESS(result) ( result == EOBIN_SUCCESS )

#define ObinCellHead \
	obin_type type;

typedef struct _ObinCell {
	ObinCellHead
} ObinCell;


ObinCell * ObinNil;
ObinCell * ObinTrue;
ObinCell * ObinFalse;
ObinCell * ObinNoValue;

#define OBIN_END_PROC return ObinNoValue

#endif
