/*
 * http://stackoverflow.com/questions/1637775/generators-in-c
 * >>> def pow2s():
      yield 1
      for i in map((lambda x:2*x),pow2s()):
        yield i
>>> def mymap(f,iter):
      for i in iter:
        yield f(i)
*/


#include <stdio.h>
#include <stdlib.h>

struct gen { // generic structure, the base of all generators
  int (*next)() ;
  int continue_from ;
} ;

typedef int (*fptr)() ;

// Each iterator has 3 components: a structure, a constructor for the structure,
// and a next function

// map

struct mapgen { // structure for map
  int (*next)() ;
  int continue_from ; // not really required, provided for compatibility
  fptr f ;
  struct gen *g ;
} ;

int map_next(struct mapgen *p) { // next function for map
  return p->f(p->g->next(p->g)) ;
}

struct gen *map(fptr f, struct gen *g) { // constructor for map iterator
  struct mapgen *p = (struct mapgen *)malloc(sizeof(struct mapgen));
  p->next = map_next;
  p->continue_from = 0;
  p->f = f;
  p->g = g;
  return (struct gen *)p ;
}


// powers of 2

struct pow2s { // structure
  int (*next)() ;
  int continue_from ;
  struct gen *g ;
};

int times2(int x) { // anonymous lambda is translated into this
  return 2*x ;
}

struct gen *pow2() ; // forward declaration of constructor

int pow2next(struct pow2s * p){ // next function for iterator
  switch(p->continue_from) {
  case 0:
    p->continue_from = 1;
    return 1;
  case 1:
    p->g = map(times2,pow2()) ;
    p->continue_from = 2;
    return p->g->next(p->g) ;
  case 2:
    p->continue_from = 2;
    return p->g->next(p->g) ;
  }
}

struct gen * pow2() { // constructor for pow2
  struct pow2s * p = (struct pow2s *)malloc(sizeof(struct pow2s));
  p->next = pow2next;
  p->continue_from = 0;
  return (struct gen *)p;
}

// in main, create an iterator and print some of its elements.

int main() {
  int i ;
  struct gen * p = pow2() ;
  for(i=0;i<10;i++)
    printf("%d ",p->next(p)) ;
  printf("\n");
}
