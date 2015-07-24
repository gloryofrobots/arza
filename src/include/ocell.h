#ifndef OCELL_H_
#define OCELL_H_
#include "ostate.h"
#include "memory/ocellmemory.h"
#include "obehavior.h"

#define OCELL_HEADER \
	OBehavior* behavior; \
	OAny origin; \
	OAny traits; \
	OCellMemoryInfo memory;

struct _ObinCell {
	OCELL_HEADER;
};

#define OCELL_DECLARE(CELLNAME, body) \
typedef struct _##CELLNAME { \
	OCELL_HEADER \
	body \
} CELLNAME

#endif /* OCELL_H_ */
