MODL
====

My Own Dumb Language

Built by following @munificent's [great guide](http://www.craftinginterpreters.com/).

Run the interpreter, call "use test;" then "fibo 5;" to see the extremely exciting value of the fifth element in the fibonacci sequence!


The language has very little syntax because reasons:

    use "filename";

just runs everything as if it were run right there. TODO: `use "filename" as namespace` to organize stuff.

To define variables:

    let name <- value;

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

is actually

    read!;

but

    map read! list;

won't work because read! won't have its `!`. (I mean, it will, because I haven't actually implemented strictly requiring the `!`, but I digress (Nor is there a map function...)).
