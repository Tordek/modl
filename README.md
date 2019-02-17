MODL
====

My Own Dumb Language

Built by following @munificent's [great guide](http://www.craftinginterpreters.com/).

Run the interpreter, call "use test;" then "fibo 5;" to see the extremely exciting value of the fifth element in the fibonacci sequence!

Syntax
------

The language has very little syntax because reasons:

    use "filename";

just runs everything as if it were run right there. TODO: `use "filename" as namespace` to organize stuff.

To define variables:

    let name <- value;

But you can define several at once:

    let name1 <- value1,
        name2 <- value2;

See below for details.

Expressions are separated by `;`, and the last one is the value returned by the whole exprression (i.e., function).

Function definition is done with:

    { arguments |
      expression1;
      expression2;
    }

When run, both are executed in order (ideally, you're a good functional boy and that's useless; however, `!` functions exist).

`!` functions are kinda special: In order to allow for zero-argument functions like `read!` (for reading input from the user), whenever the first call in an expression is a `!` function, an implicit `!` is passed:

i.e., 

    read!;

is actually parsed as

    read! !;

but

    map read! list;

won't work because read! won't have its `!`. (I mean, it won't because of other reasons, like there not being a `map` function).

Scoping
-------

Scope is where the let is.

Every assignment begins a new scope; values can't see assignments that happen later. However, within a single let, the scope is shared. This is useful for defining mutually-recursive functions, like the extremely useful...

    let odd <- { x | if (x == 0) { t | 0; } { f | even (x - 1); }; },
        even <- { x | if (x == 0) { t | 1; } { f | odd (x - 1); }; }; 
