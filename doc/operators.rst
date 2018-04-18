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