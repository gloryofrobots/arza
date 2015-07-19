#ifndef OCELLMEMORY_H_
#define OCELLMEMORY_H_
/* defined to split different gc allocators and cell struct*/
/*each allocator must provide omemory.h and ocellmemory.h files*/
/* in omemory.h must be declared _ObinMemory struct for ObinState*/
/* in ocellmemory.h _ObinCellMemory struct */

#include "../oconf.h"

typedef struct _ObinCellMemoryInfo{
	obin_bool mark;
	obin_mem_t size;
} ObinCellMemoryInfo;


#endif /* OCELLMEMORY_H_ */
