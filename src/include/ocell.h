#ifndef OCELL_H_
#define OCELL_H_
#include "ostate.h"
#include "memory/ocellmemory.h"
#include "obehavior.h"

#define OCELL_HEADER \
	OBehavior* behavior; \
	oint typeId; \
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

#define OCell_typeId(any) OAny_cellVal(any)->typeId
#define OCell_isSameType(any, type) (OCell_typeId(any) == type)

#define __OStringTypeId__ 0
#define OAny_isString(any) OCell_isSameType(any, __OStringTypeId__)
#define __OTupleTypeId__ 1
#define OAny_isTuple(any) OCell_isSameType(any, __OTupleTypeId__)
#define __OVectorTypeId__ 2
#define OAny_isVector(any) OCell_isSameType(any, __OVectorTypeId__)
#define __OTableTypeId__ 3
#define OAny_isTable(any) OCell_isSameType(any, __OTableTypeId__)
#define __OBytecodeTypeId__ 4
#define OAny_isBytecode(any) OCell_isSameType(any, __OBytecodeTypeId__)
#define __OBytesTypeId__ 5
#define OAny_isBytes(any) OCell_isSameType(any, __OBytesTypeId__)
#define __OFStreamTypeId__ 6
#define OAny_isFStream(any) OCell_isSameType(any, __OFStreamTypeId__)
#define __OIteratorTypeId__ 7
#define OAny_isIterator(any) OCell_isSameType(any, __OIteratorTypeId__)

#endif /* OCELL_H_ */
