#include <obin.h>
/*TODO remove limitations to full heap allocation */
/*#define OBIN_MEMORY_DEBUG*/

#define _end_heap(memory)  (memory->heap + memory->heap_size)
#define _heap(memory)  (memory->heap)

#define ObinMem_Padding(N) ((sizeof(opointer) - ((N) % sizeof(opointer))) % sizeof(opointer))

#define ObinMem_Malloc(n) ((omem_t)(n) > OBIN_MEM_MAX? NULL \
				: omalloc((n) ? (n) : 1))

#define ObinMem_Realloc(p, n)	((omem_t)(n) > (omem_t)OBIN_MEM_MAX  ? NULL \
				: orealloc((p), (n) ? (n) : 1))

#define ObinMem_Free ofree

#define OBIN_B_TO_KB(B) (B/(1024.0))
#define OBIN_B_TO_MB(B) ((double)B/(1024.0*1024.0))
#define OBIN_KB_TO_B(KB) (KB * 1024)
#define OBIN_MB_TO_B(MB) (MB * 1024 * 1024)

#define CATCH_STATE_MEMORY(S) \
	OMemory* M = S->memory; \
	if(!M) { opanic("ObinState memory is NULL!"); }

/*FORWARDS */

void gc_merge_free_spaces(OState*);
void init_collection_stat(OState*);
void reset_allocation_stat(OState*);

/* LOG */

OBIN_MODULE_LOG(MEMORY);

void _panic(OState* S, ostring format, ...) {
	va_list myargs;
	va_start(myargs, format);
	ovfprintf(stderr, format, myargs);
	va_end(myargs);
	oabort();
}

/************** cell initalisztion ************************************/
typedef enum _EOBIN_CELL_MARK{
	EOBIN_CELL_MARK_EMPTY=0,
	EOBIN_CELL_MARK_SET=1,
	EOBIN_CELL_MARK_NEW=2,
} EOBIN_CELL_MARK;

#define _unmark(cell) (cell->memory.mark = EOBIN_CELL_MARK_EMPTY)
#define _mark(cell) (cell->memory.mark = EOBIN_CELL_MARK_SET)
#define _marknew(cell) (cell->memory.mark = EOBIN_CELL_MARK_NEW)

#define _is_marked(cell) (cell->memory.mark == EOBIN_CELL_MARK_SET)
#define _is_not_marked(cell) (cell->memory.mark == EOBIN_CELL_MARK_MARKED)
#define _is_new(cell) (cell->memory.mark == EOBIN_CELL_MARK_NEW)

OAny OCell_toAny(EOTYPE type, OCell* cell) {
	OAny result;
	oassert(OType_isCell(type));
	result = OAny_new(type);
	OAny_cellVal(result) = cell;
	return result;
}

OAny OCell_new(EOTYPE type, OCell* cell, OBehavior* behavior, OAny origin) {
	OAny result;
	oassert(OType_isCell(type));

	cell->origin = origin;
	cell->behavior = behavior;
	_unmark(cell);

	result = OAny_new(type);
	OAny_cellVal(result) = cell;

	return result;
}

/* MEMORY PRIMITIVES */
opointer omemory_malloc(OState * S, omem_t size) {
	opointer new_pointer;

	if (!size) {
		return NULL;
	}

	new_pointer = ObinMem_Malloc(size);
	if(!new_pointer) {
    	_log(S, _ERR,"Failed to allocate the initial %d bytes for the GC. Panic.\n",
                (int) size);

    	oabort();
    	return NULL;
	}

	memset(new_pointer, 0, size);
	return new_pointer;
}

opointer omemory_realloc(OState * S, opointer ptr, omem_t size) {
	opointer new_pointer;
	if (!size) {
		return NULL;
	}

	new_pointer = ObinMem_Realloc(ptr, size);
	assert(new_pointer != 0);
	return new_pointer;
}

opointer obin_memory_duplicate(OState * S, opointer ptr,
		omem_t elements, omem_t element_size) {
	opointer new_pointer;
	omem_t size;

	size = element_size * elements;

	new_pointer = omemory_malloc(S, size);
	memcpy(new_pointer, ptr, size);

	return new_pointer;
}

/* GC and Allocator */

void _memory_create(OState* S, omem_t heap_size) {
	OMemory* M;
	if(heap_size >= OBIN_MAX_HEAP_SIZE) {
		_panic(S, "obin_state_new heap_size %d too big for current configuration,"
				" check OBIN_MAX_HEAP_SIZE in oconf.h",
				heap_size);
	}

	S->memory = (OMemory*) omemory_malloc(S, sizeof(OMemory));
	M = S->memory;

	if(!M) {
		opanic("Not enough memory to allocate State");
	}

    M->heap_size = heap_size;

    /* Buffersize is adjusted to the size of the heap (10%) */
    M->heap_gc_threshold = (int) (M->heap_size * 0.1);

    /* allocation of the heap */
    M->heap = ObinMem_Malloc(M->heap_size);
    if (!M->heap) {
    	_panic(S, "Failed to allocate the initial %d bytes for the GC. Panic.\n",
                (int) M->heap_size);
    }

    omemset(M->heap, 0, M->heap_size);
    M->heap_free_size = M->heap_size;

    /* initialize free_list by creating the first */
    /* entry, which contains the whole object_space */
    M->free_node = (OMemoryFreeNode*) M->heap;
    M->free_node->size = M->heap_size;
    M->free_node->next = NULL;

    /* initialise statistical counters */
    M->collections_count = 0;

    /* these two need to be initially set here, as they have to be preserved */
    /* across collections and cannot be reset in init_collect_stat() */
    M->allocated_count = 0;
    M->allocated_space = 0;
}

void _memory_destroy(OState* S) {
	ObinMem_Free(S->memory->heap);
	ObinMem_Free(S->memory);
	S->memory = 0;
}

OState* OState_create(omem_t heap_size) {
	OState* S;
	omem_t size;
    size = sizeof(OState);
	S = ObinMem_Malloc(size);
	if(!S) {
    	opanic("Failed to allocate ObinState");
    	return NULL;
	}

	memset(S, 0, size);

	_memory_create(S, heap_size > 0 ? heap_size: OBIN_DEFAULT_HEAP_SIZE);
	return S;
}

void OState_destroy(OState* S) {
	ObinMem_Free(S->memory->heap);
    ObinMem_Free(S->memory);
	ObinMem_Free(S);
}

/**
 *  check whether the object is inside the managed heap
 *  if it isn't, there is no VMObject to mark, otherwise
 *  check whether the object is already marked.
 *  if the self is an unmarked object inside the heap, then
 *  it is told to 'mark_references', recursively using this
 *  function for all its references.
 */
static OAny gc_mark_object(OState* S, OAny object) {
	OCell* cell = OAny_cellVal(object);
	CATCH_STATE_MEMORY(S);
	if(!cell) {
		return ObinNil;
	}

    if (   ((void*) cell < (void*)  _heap(M))
        || ((void*) cell > (void*) _end_heap(M)))
    {
    	/*ObinNil, ObinFalse, ObinTrue, integers etc */
		return ObinNil;
    }

	if (_is_marked(cell) || _is_new(cell)) {
		return ObinNil;
	}

	_mark(cell);
	M->live_count++;
	M->live_space += cell->memory.size;

	if(!cell->behavior) {
		_log(S, _WARN, "GC encountered object without behavior");
		return ObinNil;
	}

	if(!cell->behavior->__mark__) {
		return ObinNil;
	}

	cell->behavior->__mark__(S, object, &gc_mark_object);

	return ObinNil;
}

void gc_mark_reachable_objects(OState * S) {
	OAny globals = S->globals;
	gc_mark_object(S, globals);

	/*     Get the current frame and mark it.
    Since marking is done recursively, this automatically
	marks the whole stack
    pVMFrame current_frame = (pVMFrame) Interpreter_get_frame();
    if (current_frame != NULL) {
        gc_mark_object(current_frame);
    }*/
}

static void _destroy_cell(OState * S, OCell* cell) {
	if (!cell) {
		opanic("cell is null");
	}

	if(!cell->behavior
			|| !cell->behavior->__destroy__) {

		return;
	}

	cell->behavior->__destroy__(S, cell);
}


void omemory_collect(OState* S) {
	opointer pointer;
	OCell* object;
	OMemoryFreeNode* current_entry, *new_entry;
    int object_size = 0;
	CATCH_STATE_MEMORY(S);

	if(S->memory->transaction_count != 0) {
		_log(S, _INFO, "obin_gc_collect skip collection because memory transaction [%d] is in progress \n",
				S->memory->transaction_count);
		return;
	}

    M->collections_count++;
    init_collection_stat(S);

    gc_mark_reachable_objects(S);

#ifdef OBIN_MEMORY_DEBUG
	_log(S, "-- pre-collection heap dump --\n");
	omemory_debug_trace(S);
#endif

    pointer = M->heap;
    current_entry = M->free_node;
    do {
        /* we need to find the last free entry before the pointer */
        /* whose 'next' lies behind or is the pointer */
        while (((void*)pointer > (void*)current_entry->next) && (current_entry->next != NULL)) {
            current_entry = current_entry->next;
        }

        if (((void*)current_entry->next == (void*)pointer) || ((void*)current_entry == (void*)pointer)) {
            /* in case the pointer is the part of the free_list: */
            if ((void*)current_entry == (void*)pointer) {
                object_size = current_entry->size;
            } else {
                OMemoryFreeNode* next = current_entry->next;
                object_size = next->size;
            }
            /*fprintf(stderr,"[%d]",object_size); */
            /* nothing else to be done here */
        } else {
            /* in this case the pointer is a VMObject */
            object = (OCell*) pointer;
            object_size = object->memory.size;
            /* is this object marked or not? */
            if (_is_marked(object)) {
                /* remove the marking */
            	_unmark(object);
            	/* skip new objects */
            } else if(!_is_new(object)) {
                M->killed_count++;
                M->killed_space += object_size;
                /* add new entry containing this object to the free_list */
                _destroy_cell(S, object);
                memset(object, 0, object_size);
                new_entry = ((OMemoryFreeNode*) pointer);
                new_entry->size = object_size;

                /* if the new entry lies before the first entry, */
                /* adjust the pointer to the first one */
                if (new_entry < M->free_node) {
                    new_entry->next = M->free_node;
                    M->free_node = new_entry;
                    if(!M->free_node) {
                    	_panic(S, "free node is NULL");
                    }
                    current_entry = new_entry;
                } else {
                    /* insert the newly created entry right after the current entry */
                    new_entry->next = current_entry->next;
                    current_entry->next = new_entry;
                }
            }
        }
        /* set the pointer to the next object in the heap */
        pointer = (void*)((int)pointer + object_size);

    } while ((void*)pointer < (void*)(_end_heap(M)));

    /* combine free_entries, which are next to each other */
    gc_merge_free_spaces(S);

#ifdef OBIN_MEMORY_DEBUG
	_log(S, "-- post-collection heap dump --\n");
	omemory_debug_trace(S);
#endif
    reset_allocation_stat(S);
}


void* _allocate_cell(OState* S, omem_t size) {
    void* result = NULL;
	OMemoryFreeNode* entry, *before_entry, *old_next, *replace_entry;
	int old_entry_size;
	CATCH_STATE_MEMORY(S);

    if(size == 0) {
    	return NULL;
    }

    if(size < sizeof(OMemoryFreeNode)) {
    	_panic(S, "Can`t allocate so small chunk in allocator %d", size);
    	return NULL;
    }

    if (M->heap_free_size <= M->heap_gc_threshold) {
    	omemory_collect(S);
    }

    /* initialize variables to search through the free_list */
    entry = M->free_node;
    before_entry = NULL;

    /* don't look for the perfect match, but for the first-fit */
    while (! ((entry->size == size)
               || (entry->next == NULL)
               || (entry->size >= (size + sizeof(OMemoryFreeNode))))) {
        before_entry = entry;
        entry = entry->next;
    }

    /* did we find a perfect fit? */
    /* if so, we simply remove this entry from the list */
    if (entry->size == size &&  entry->next != NULL) {
        if (entry == M->free_node) {
            /* first one fitted - adjust the 'first-entry' pointer */
            M->free_node = entry->next;
            if(!M->free_node) {
            	_panic(S, "Free node is null");
            }
        } else {
            /* simply remove the reference to the found entry */
            before_entry->next = entry->next;
        } /* entry fitted */
        result = entry;

    } else {
        /* did we find an entry big enough for the request and a new */
        /* free_entry? */
        if (entry->size >= (size + sizeof(OMemoryFreeNode))) {
            /* save data from found entry */
            old_entry_size = entry->size;
            old_next = entry->next;

            result = entry;
            /* create new entry and assign data */
            replace_entry =  (OMemoryFreeNode*) ((int)entry + size);

            replace_entry->size = old_entry_size - size;
            replace_entry->next = old_next;
            if (entry == M->free_node) {
                M->free_node = replace_entry;
				if(!M->free_node) {
					_panic(S, "free node is NULL");
				}
            } else {
                before_entry->next = replace_entry;
            }
        }  else {
            /* no space was left */
            /* running the GC here will most certainly result in data loss! */
            _log(S, _WARN, "Not enough heap!\n");
            _log(S, _WARN, "FREE-Size: %d Perfoming garbage collection\n", M->heap_free_size);

            omemory_collect(S);

            _log(S, _WARN, "FREE-Size after collection: %d,\n", M->heap_free_size);
            if(M->heap_free_size <= size) {
            	_panic(S, "Failed to allocate %d bytes. Heap size %d \n", (int)size, M->heap_free_size);
            }

            /*fulfill initial request */
            result = _allocate_cell(S, size);
        }
    }

	if(!result) {
        _panic(S, "Failed to allocate %d bytes. Panic.\n", (int)size);
    }

    memset(result, 0, size);
    /* update the available size */
    M->heap_free_size -= size;
    return result;
}

void* omemory_allocate_cell(OState* S, omem_t size) {
	omem_t aligned_size = size + ObinMem_Padding(size);
    OCell* object = (OCell*)_allocate_cell(S, aligned_size);

    if(!object) {
    	return NULL;
    }

    object->memory.size = aligned_size;
    _marknew(object);
    S->memory->allocated_count++;
    S->memory->allocated_space += aligned_size;
    return object;
}


/**
 * this function must not do anything, since the heap management
 * is done inside gc_collect.
 */
void omemory_free(OState* S, opointer ptr) {
#ifdef ODEBUG
	CATCH_STATE_MEMORY(S);
    /* check if called for an object inside the object_space */
    if ((   ptr >= (void*)  M->heap)
        && (ptr < (void*) (M->heap + M->heap_size)))
    {
    	opanic("free called for an object in allocator");
    }
#endif
    ObinMem_Free(ptr);
}

/* free entries which are next to each other are merged into one entry */
void gc_merge_free_spaces(OState* S) {
	OMemory* M = S->memory;
    OMemoryFreeNode* entry = M->free_node;
    OMemoryFreeNode* entry_to_append = NULL;
    int new_size = 0;
    OMemoryFreeNode* new_next = NULL;

    M->heap_free_size = 0;

    while (entry->next != NULL) {
        if (((int)entry + (int)(entry->size)) == (int)(entry->next)) {
            entry_to_append = entry->next;
            new_size = entry->size + entry_to_append->size;
            new_next = entry_to_append->next;

            memset(entry_to_append, 0, entry_to_append->size);

            entry->next = new_next;
            entry->size = new_size;
        } else {
            M->heap_free_size += entry->size;
            entry = entry->next;
        }
    }
    if (entry->next == NULL) {
        M->heap_free_size += entry->size;
    } else {
    	_panic(S, "Missed last free_entry of GC\n");
    }
}
/**
 * if this counter is gt zero, an object initialization is
 * in progress. This means, that most certainlt, there are
 * objects, which are not reachable by the rootset, therefore,
 * the garbage collection would result in data loss and must
 * not be started!
 */
void omemory_start_transaction(OState* S) {
    S->memory->transaction_count++;
}

/**
 * only if the counter reaches zero, it is safe to start the
 * garbage collection.
 */
void omemory_end_transaction(OState* S) {
    S->memory->transaction_count--;
}

/*
 functions for GC statistics and debugging output
 * initialise per-collection statistics
 */
void init_collection_stat(OState* S) {
	CATCH_STATE_MEMORY(S);
    /* num_alloc and spc_alloc are not initialised here - they are reset after
     * the collection in reset_alloc_stat() */
    M->live_count = 0;
    M->live_space = 0;
    M->killed_count = 0;
    M->killed_space = 0;
}

/*
 * reset allocation statistics
 */
void reset_allocation_stat(OState* S) {
	CATCH_STATE_MEMORY(S);
    M->allocated_count = 0;
    M->allocated_space = 0;
}

/*
 * output per-collection statistics
 */
static void _log_memory_stat(OState* S) {
	CATCH_STATE_MEMORY(S);
    _log(S, _ALL, "\n[State %p memory. Heap size %d B (%.2f kB, %.2f MB)\n"
    		" collections:%d,\n %d allocated in (%d B %.2f kB), \n %d live in (%d B %.2f kB), %d killed in "\
            "(%d B %.2f kB)]\n ", S,
        M->heap_size, OBIN_B_TO_KB(M->heap_size), OBIN_B_TO_MB(M->heap_size),
        M->collections_count,
		M->allocated_count, M->allocated_space, OBIN_B_TO_KB(M->allocated_space),
		M->live_count, M->live_space, OBIN_B_TO_KB(M->live_space),
        M->killed_count, M->killed_space, OBIN_B_TO_KB(M->killed_space));
}
/**
 * For debugging - the layout of the heap is shown.
 * This function uses
 * - '[size]' for free space,
 * - '-xx-' for marked objects, and
 * - '-++-' for new objects
 * - '-size-' for unmarked objects.
 * The output is also aligned to improve readability.
 */
static void _memory_trace(OState* S) {
    OCell* pointer;
    OMemoryFreeNode* current_entry;
    int object_size = 0;
    int object_aligner = 0;
    int line_count = 2;
    OCell* object;
	CATCH_STATE_MEMORY(S);

    pointer = M->heap;
    current_entry = M->free_node;
    if(!current_entry) {
    	return;
    }

    _log(S, _ALL, "\n########\n# SHOW #\n########\n");

    do {
        while (((void*)pointer > (void*)current_entry->next) && (current_entry->next != NULL)) {
            current_entry = current_entry->next;
        }

        if ((   (void*)current_entry->next == (void*)pointer)
            || ((void*)current_entry == (void*)pointer))
        {
            if ((void*)current_entry == (void*)pointer) {
                object_size = current_entry->size;
            } else {
                OMemoryFreeNode* next = current_entry->next;
                object_size = next->size;
            }
            _log(S, _ALL, "[%d]",object_size);
        } else {
            object = pointer;

            /*here we need recursive function maybe*/
            object_size = object->memory.size;

            /* is this object marked or not? */
            if (_is_marked(object)) {
            	_log(S, _ALL, "-xx-");
            } else if (_is_new(object)) {
            	_log(S, _ALL, "-++-");
            }

            _log(S, _ALL, "-%d %s %p-", object_size, _is_new(object) ? "" : object->behavior->__name__, object);
        }
        /* aligns the output by inserting a line break after 36 objects */
        object_aligner++;
        if (object_aligner == 36) {
            _log(S, _ALL, "\n%d ", line_count++);
            object_aligner = 0;
        }
        _log(S, _ALL, "\n");
        pointer = (void*)((int)pointer + object_size);
    } while ((void*)pointer < (void*)(_end_heap(M)));
}

void omemory_debug_trace(OState* S) {
	_log_memory_stat(S);
	_memory_trace(S);
}
