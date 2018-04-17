Import and Export
=================

.. highlight:: arza

Arza uses files as modules. Modules in Arza could be used as top level objects with methods but
most of the time there are no need for this. Instead arza treats modules as namespaces or mixins.
You include objects  from one module to another and give to this objects specific prefix to avoid conflicts


::
    
    // import qualified names (prefixed by module name)
    import seq
    import io

    // Afterwards, all exported names from this modules available as qualified names
    let _ = io:print(seq:reverse([1,2,4,5]))

    // import other module
    import my:modules:module1

    // only last part of module identifier used as qualifier
    let three = module1:add(1, 2)

    // use aliases to resolve name conflicts
    import my:modules:module1 as mod1
    import my:module1 as mod1_1

    let x = mod1:add(mod1_1:add(1, 2), 3)

    // import only required qualified names
    import my:module1 (f1 as f1_1, f2 as f2_1)
    let _ = module1:f1_1()
    let _ = module1:f2_1()

    import my:modules:module1 as mod1 (f1, f2)
    let _ = mod1:f1()
    let _ = mod1:f2()

    import my:module1 as mod1 (f1 as f1_1, f2 as f2_1)
    let _ = mod1:f1_1()
    let _ = mod1:f2_1()

    // binding funcs from two modules to same name if there are no conflicts between them
    import tests:lib_az:abc:ts:module_s as s
    import tests:lib_az:abc:ts:module_t as s

    // hiding names
    import my:modules:module1  hiding (CONST)
    let _ = module1:f1()
    let _ = module1:f2()

    import my:modules:module1 as mod1 hiding (f1)
    let _ = mod1:f2()
    let _ = mod1:CONST

    import tests:lib_az:abc:module_ab as ab5 hiding (f_ab, CONST)

    /// UNQUALIFIED IMPORT
    // import specified unqualified names
    include my:modules:module1 (f1, f2, CONST as const) 
    let _ = f1()
    let x = f2() + const

    // import all unqualified names from module

    include my:modules:module1 

    // hiding specific names
    include my:modules:module1 hiding (CONST)
    let x = f1() * f2()


Also module can specify export list to forbid acces to private values

::

    // By default all names except operators can be imported outside
    // You can limit it with export expression
    let CONST = 41
    fun f_ab () = CONST + 1
    fun f_ab_2 = f_ab()

    export (f_ab, f_ab_2, CONST)

Loading Order
-------------
Lets consider what happens when running such arza like

::

   python arza.py /root/home/coder/dev/main.arza

* compiler imports module prelude.arza 
  If prelude is absent execution will be terminated.
  All names from prelude will be available as builtins for other modules
* compiler imports rest of standart library (list, tuple, map, ...etc)
* interpeter compiles file :code:`/root/home/coder/dev/main.arza`, finds in this script function
  :code:`fun main()` and executes it

How do Arza resolve module imports?
When compiler parses expression :code:`import(include) module1.module2.mymodule`
it tries to find this module in global cache.
If module is absent compiler  transforms it's name to path "module1/module2/mymodule.arza".
Then it will look for this path in specific order

* Main program folder. If you ran arza as :code:`python arza.py /root/home/coder/dev/main.arza`
  this directory would be :code:`/root/home/coder/dev/`
* Lib folder. This is directory __lib__ inside script folder  :code:`/root/home/coder/dev/__lib__`
* Arza standart library. This is directory from environment variable ARZASTD. If this var is empty
  all required modules must be located in __lib__ directory

If file is found Arza will load it, compile it and store it in global state.
Modules always have unique names throughout all program.
Relative imports are not possible. Modules are loaded only once. 