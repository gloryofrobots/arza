#ifndef OCELL_H_
#define OCELL_H_
#include "ostate.h"
#include "memory/ocellmemory.h"
#include "obehavior.h"

#define OBIN_CELL_HEADER \
	OBehavior* behavior; \
	OAny origin; \
	OAny traits; \
	ObinCellMemoryInfo memory;

struct _ObinCell {
	OBIN_CELL_HEADER;
};

#define OBIN_DECLARE_CELL(CELLNAME, body) \
typedef struct _##CELLNAME { \
	OBIN_CELL_HEADER \
	body \
} CELLNAME

#endif /* OCELL_H_ */
