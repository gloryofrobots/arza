#ifndef TEST_MEMORY_H_
#define TEST_MEMORY_H_
#include <obin.h>

typedef struct {
 obin_mem_t Count;
 obin_mem_t TotalCount;
 obin_mem_t Marked;
 obin_mem_t TotalMarked;
 obin_mem_t Destroyed;
 obin_mem_t TotalDestroyed;

 obin_mem_t OldMarked;
} TMCounter;

void tm_counter_destroy(TMCounter* counter) {
	counter->TotalDestroyed++;
	counter->Destroyed++;
}

void tm_counter_mark(TMCounter* counter) {
	counter->TotalMarked++;
	counter->Marked++;
}

void tm_counter_add(TMCounter* counter) {
	counter->TotalCount++;
	counter->Count++;
}

void tm_counter_refresh(TMCounter* counter) {
	counter->Count = 0;
	counter->Marked = 0;
	counter->Destroyed = 0;
}

void tm_counter_remember(TMCounter* counter) {
	counter->OldMarked = counter->Marked;
}

obin_mem_t tm_counter_predict_destroyed(TMCounter* counter) {
	return (counter->Count - counter->Marked) + counter->OldMarked;
}

void tm_counter_info(TMCounter* counter) {
	 printf("TMCounter count %d \n", counter->Count);
	 printf("TMCounter marked %d \n", counter->Marked);
	 printf("TMCounter destroyed %d \n", counter->Destroyed);
	 printf("TMCounter predict destroyed %d \n", tm_counter_predict_destroyed(counter));
}

TMCounter* tm_counter_new() {
	TMCounter* counter = malloc(sizeof(TMCounter));
	memset(counter, 0, sizeof(TMCounter));
	return counter;
}

void tm_counter_free(TMCounter* counter) {
	free(counter);
}


#endif /* TEST_MEMORY_H_ */
