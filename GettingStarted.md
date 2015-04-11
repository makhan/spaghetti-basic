# Getting started #

This is a brief introduction to Spaghetti, discusses writing simple programs and
the basics of Spaghetti syntax.

Note, Spaghetti is currently in a very early stage. There are a lot of errors in the interpreter code. Furthermore, any syntax or other errors in the code being run will simply cause the interpreter to throw an exception and shut down without posting many helpful error messages about what went wrong with your code.

Keep in mind that Spaghetti is not meant to be a serious programming language.

## "Hello, world" in Spaghetti ##

In Spaghetti, a simple "Hello, world" program would look like this:

```
10 PRINT "Hello, world"
20 END
```

To actually run this program, write it into a text file in any editor and save it as
helloworld.bas. To run it, simply type `./spaghetti.py helloworld.bas` at the terminal.
Currently, spaghetti does not come with an installer/setup tool, so you would have to run
`./spaghetti.py` from the same directory where you have the spaghetti.py file.

Some things about the syntax that are obvious from the above example:
  * Spaghetti uses line numbers
  * Text within double quotes are String literals
  * Programs terminate when the END statement is encountered

Another thing to note is that Spaghetti considers source files to be case sensitive. So,
while `PRINT` is a keyword, you can still declare a variable called `print`.

_Note: Using line numbers is not really necessary for every line, only target lines for GOTO and GOSUB need line numbers_
## Variables and Data Types ##

Spaghetti supports the following data types:

  * INTEGER: Roughly equivalent to a signed 32 bit int in C
  * BOOLEAN: A data type whose value can only be 0 or 1
  * STRING: A special data type that can hold a string. There are no restrictions (other than those of the underlying implementation) on the length.
  * DOUBLE: Floating point type, equivalent to a C double.

Variables can be declared using the DIM statement. A simple variable declaration looks
like this:

```
10 DIM some_var AS DOUBLE
```

This creates a variable called `some_var` of type `DOUBLE`. To declare a variable of some
other type, simply substitute `DOUBLE` to be the required type.

You can also omit the data type altogether, in that case the data type is assumed to be
an INTEGER.

```
10 DIM xyz
```

Trying to assign a value of different data type result in an implicit cast (i.e. the
value is casted to the datatype of the variable, with possible loss of data), or an error
in case the cast fails.

Finally, you can omit the declaration altogether. Simply assigning a value to a variable
that has not been declared causes the variable to be automatically created and have the
same time as the value it is being assigned.

```
10 pi=3.14159
```

This is equivalent to

```
10 DIM pi AS DOUBLE
20 pi=3.14159
```

Although assigning results in automatic variable declaration, the type of the variable
remains the same throughout the rest of the program. Thus, any subsequent assignments to
it do not change its type and are subject to implicit casting.

## GOTO ##

A `GOTO` statement moves execution to different line.

```
10 PRINT "Hello"
20 GOTO 40
30 PRINT "world"
40 END
```

This only prints "Hello". The `GOTO` in line 20 move execution to line 40, skipping 30
and so not printing "world".

## GOSUB/RETURN ##

A `GOSUB` works much like a `GOTO`, but it also remembers where the `GOSUB` was called
from. After executing a `GOSUB`, the program is executed sequentially from the target
line number, until a `RETURN` is encountered. The `RETURN` statement is like a reverse
`GOSUB`, it takes execution back to the line after the last `GOSUB`.

### `GOSUB`/`RETURN` Example ###
```
10 x=10
20 m=1.2
30 c=0
40 GOSUB 100
50 x=-5
60 m=100
70 c=-9
80 GOSUB 100
90 END
100 REM target of GOSUB
110 y=m*x+c
120 PRINT y
130 RETURN
```

Put together, a block of code within the target of a `GOSUB` and a `RETURN` is a like a
very primitive form of a function.

## Conditional Statements ##

Spaghetti supports simple single line `IF-THEN-ELSE` constructs. The part following the
`IF` has to be an expression that is evaluated and cast to a `BOOLEAN`. The value of that
expression (0 or 1) determines whether the statement following the `THEN` or that
following the `ELSE` is executed. The `ELSE` is actually optional, it can be missing if
there is nothing to be done if the expression is 0.

```
10 A=10
20 IF A>5 THEN A=A-5 ELSE PRINT A
30 IF A>0 THEN GOTO 20
40 END
```

## Expressions and Assignments ##

Expressions in Spaghetti can be formed by variables of any data type on which various
binary or unary operations, or built in functions, are applied. They can include any
number of nested expressions in parentheses.

The allowed (binary) operators are: '+','-','**','/','%','AND','OR','XOR','=','>',
'<','<>','>=','<='**

The only unary operators are: '-' (unary minus) and 'NOT'

Assignment statements are of the form: `LET` variable = expression
As in the examples before, the `LET` keyword can be omitted

## Arrays ##

Spaghetti supports multidimensional arrays. Arrays are declared just like any other
variable, but with the dimensions and lengths of each dimension as a comma separated list
within parentheses after the variable name.

```
10 DIM myArray AS INTEGER(3,3) REM Declares a 3x3 2D array
20 DIM singleArray AS STRING(10) REM Declares a 1D array of length 10
```

Array declaration is not optional, unlike scalar variables. All arrays have to be
declared, simply assigning to an array does not cause it to be created.

Unlike most other BASICs, Spaghetti's arrays are 0 based. A length N array starts from 0
and goes upto N-1.

Indexing an array is done by specifying the index as a comma separated list of integers
within parentheses.

```
10 DIM matrix AS INTEGER(2,2)
20 matrix(0,0)=1
30 matrix(0,1)=0
40 matrix(1,0)=1
50 matrix(1,1)=0
60 PRINT matrix(1,0)
70 END
```

## Displaying Output ##

Currently the only way of producing any output from a Spaghetti program is by printing to
stdout by the `PRINT` statement. `PRINT` is a statement and not a function, so it does
not require parentheses.

The simplest use of `PRINT` would be:

```
10 PRINT "abcd"
```

But `PRINT` can be given a list of items to print.

```
10 PRINT "abcd","xyz",10,7.2
```

A trailing comma after the last item causes `PRINT` to suppress the newline that it
normally prints.

```
10 PRINT "abcd","xyz",10,7.2, 
```

The items to be printed can actually be any expression rather than just variables or
literals.

```
10 PRINT 1+2,"ab"+"cd",6/3
```

## Getting Input ##

Like the `PRINT` statement, the primary way of getting any external input in Spaghetti at this stage is by reading data from stdin using the `INPUT` statement. This is also a statement rather than a function call.

`INPUT` works very much like the `PRINT` statement in that it also takes a list of variables as its argument. It then reads one token (a non-empty sequence of non-whitespace characters) from stdin for each variable. Each token is automatically converted from a string into whatever type the variable it is going into has.

Another method is the `INPUTLINE` statement. This is essentially the same as `INPUT` but it reads entire lines at a time instead of tokens. This useful in reading strings that may contain spaces in them.


```
10 DIM firstname AS STRING
20 DIM secondname AS STRING
30 INPUT firstname
40 INPUT secondname
50 PRINT "Hello ",firstname,secondname
60 END
```

## Comments ##

In Spaghetti comments can be added by using the `REM` key word. Anything after a `REM`
and up to the next newline is considered a comment and ignored by the parser.

## The `END` Keyword ##

Program execution stop immediately when an `END` statement is encountered. If an `END` is
not encountered, but the program has finished the last line, the program still terminates
without the need for `END`. But it is usually  good idea to have an `END` just to clearly
mark a point where the program terminates.

`END` is particularly useful when a program needs to stop even when there are lines after
the `END` statement.

```
10 PRINT "END Example"
20 GOSUB 40
30 END
40 REM GOSUB block starts here
50 PRINT "Inside GOSUB"
60 RETURN
```


## Extras ##

Spaghetti also has a small library of built in functions. This includes common functions such as SIN, ABS, and SORT, and are basically implemented as simple wrappers over Python functions. Most commonly used BASIC functions are available in Spaghetti, and usually have the same names as in any other dialect of BASIC (e.g. UCASE, MID, LTRIM, etc.). A separate list of functions will likely be added to the wiki once the library code stabilizes, but until then a read of the standard\_library.py file will make all available functions apparent.

From version 0.2.1, Spaghetti supports a very limited form of FOR loop. This was added as a sort of last minute hack on top of the language and is not really built into the parser. Basically something akin to a preprocessor tries to convert any FOR loops into equivalent code using IFs and GOTOs. Since this is not implemented at a parser level, it will not work a lot of the time, especially with expressions forming loop counter start and termination values. It is safer to just use GOTOs until proper loop syntax is added.