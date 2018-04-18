Operators
=========

.. highlight:: arza

You can define custom operators in prelude global to all modules,
or define them locally in you module for your module only.

Some of the operators like :code:`:: . : and or -> #`
are declared internally and have special meaning for compiler

All defined operators in prelude

::

    // first name is operator, second is function which be used by compiler and third is precedence 
    // right binding
    infixr (:=, :=, 10)

    // internal infix as of precedence 15

    infixr (<-, <-, 15)
    infixr (!, __send__, 15) // sending message
    infixl (<|, <|, 15) // pipe left
    infixl (|>, |>, 20) // pipe right

    // internal infix or precedence 25

    infixl (<<, <<, 25) // func composition left
    infixl (>>, >>, 25) // func composition right

    // internal infix and precendece 30

    infixl (<, <, 35)
    infixl (>, >, 35)
    infixl (>=, >=, 35)
    infixl (<=, <=, 35)
    infixl (==, ==, 35)
    infixl (!=, !=, 35)
    infixl (++, ++, 40)
    infixl (+, +, 40)
    infixl (-, -, 40)
    infixl (*, *, 50)
    infixl (/, /, 50)

    // prefix operator
    // cannot use - it is set for infix operator
    // use qualified name to prevent infinite loops in cases of declaring local negate function using prefix -
    prefix (-, arza:negate, 55)

    // internal infix :: precedence 60

    infixl (**, **, 60) // pow

    // internal prefix # precedence 70

    prefix (&, &, 70) // deref
    prefix (&&, &&, 70) //deref deref
    infixl (.., .., 90) // carrying

    // internal infix (  .{ .[ precedence 95

    prefix (~, ~, 96) // carried function

    // internal infix . : precedence 100


Later you must create functions for declared operators like

::
    
    fun |>(x, f) = f(x)
    fun <|(f, x) = f(x)
    fun >>(f, g) = x -> g(f(x))
    fun <<(f, g) = x -> f(g(x))
    // ... and others


When Arza parses expression :code:`1 + 2` it compiles it to :code:`+(1, 2)`.

The same with prefix operator. Expression :code:`-1` will be transformed into :code:`arza:negate(1)`

Special operators
-----------------

* infix operator :code:`:` like in :code:`module:function()` treats by compiler as exported name
  and as path separator in :code:`import include` expressions

  ::

    import my:modules:module1
    let three = module1:add(1, 2)
  
* infix operators :code:`and or`  are compiled into jump instructions

* infix operator :code:`->`  creates lambda functions like :code:`(x, y) -> x + y`

* infix operator :code:`::`  compiles into call :code:`cons(left, right)` in expressions and
  receives special treatment in pattern matching

* infix operator :code:`of`  compiles into call :code:`kindof(left, right)` in expressions and
  receives special treatment in pattern matching

* infix operator :code:`as`  compiles into call :code:`cast(left, right)` in expressions and
  receives special treatment in pattern matching

* infix operator :code:`.` like in :code:`left.right` compiles into :code:`at(left, #right)` where
  :code:`#right` is symbol


* infix operator :code:`.[` like in :code:`left.[right]` compiles into :code:`at(left, right)` where
  :code:`right` is any expression

* infix operator :code:`.{` like in :code:`left.{key=value}` compiles into :code:`put(left, #key, value)`.
  If :code:`key` is enclosed in parens like :code:`left.{(key) = value}`
  it compiles to :code:`put(left, key, value)`.

  ::

     let x = {x=1, (1+2)=2}
     let x1 = x.{x=2, (True)=2, (4-1)=2, "key"="value"}

* infix operator :code:`(` like in :code:`myfunc(ar1, arg2)` compiles into special bytecode instruction and
  receives special treatment in pattern matching

* infix operator :code:`{` like in :code:`MyType{key1=value1, key2}` receives special treatment in pattern matching

* infix operator :code:`|` delimits clauses in pattern matching

* prefix operator :code:`not` compiles  into special instruction

* prefix operator :code:`#` like in :code:`#I_AM_SYMBOL`
  constructs  symbols in expressions and in match clauses 


* prefix operator :code:`...` like in :code:`[x, x1, ...xs]` and :code:`myfunc(...varargs)`
  receives special treatment in pattern mathing and in function calls

::

   match [1, 2, 3]
   | [head, ...tail]

   fun f(...args) =
       //calling other func 
       // ...args flush sequence into call arguments
       f2(1, 2, ...args, 3, 4)
   

Functions as infix operators
----------------------------

To call function as infix operator enclose it in \`\`.

**Such function operator will have precedence 35**

::

   mymap `has` #key
   i `kindof` Int
   1 `add` 2