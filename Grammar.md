# Grammar #

Spaghetti's grammar is based on old BASICs. All lines must have line numbers (although that is not a grammar element and therefore not shown here), and there are no subs/functions or even a `FOR` `NEXT` syntax. All looping/calling is done via `GOTO` and `GOSUB`. It does however support arbitrarily nested `IF-THEN-ELSE` constructs in a single line.

Spaghetti also supports arrays and a small set of built-in functions. Array and function call syntax are the same, placing indexes or arguments inside parentheses after the array/function name.

`PRINT` and `INPUT` are statements rather than function calls in Spaghetti. This is partly due to the fact that all function calls require arguments in parentheses, and having `PRINT` and `INPUT` not need them was important to making Spaghetti's syntax remain more BASIC-like.

The complete grammar is given below.

```
<program> ::= <line> | <line> \n <line>
<line> ::= <statement>

<statement> ::= <expression> | <branch> | <jump> | <call> | <return> | <declaration> | <end> | <output> | <input> | <line input> | <assignment> 

<branch> ::= IF <expression> THEN <statement> | IF <expression> THEN <statement> ELSE <statement>
<jump> ::= GOTO <expression>
<call> ::= GOSUB <expression>
<return> ::= RETURN
<declaration> ::= DIM <identifier> AS <datatype>
<end> ::= END
<output> ::= PRINT <list> | PRINT <list> ,
<input> ::= INPUT <list>
<line input> ::= INPUTLINE <list>
<assignment> ::= LET <identifier> = <expression> | <identifier> = <expression>

<list> ::= <expression> | <expression> , <list>

<expression> ::= <boolean_expr> <boolean_op> <expression> | <boolean_expr> 
<boolean_expr> ::= <value> <relational_op> <expression> | <value>
<value> ::= <term> <add_sub_op> <expression> | <term>
<term> ::= <factor> <mul_div_op> <expression> | <factor>
<factor> ::= ( <expression> ) | <base_value>
<base_value> ::= NOT <factor> | - <factor> | <identifier> | <literal>

<identifier> ::= <identifier_token> ( <list> ) | <identifier_token>
<literal> ::=  " <string> " | <number>
<string> ::= any sequence of 0 or more characters except a '"'
<number> :: <integer> | <integer> . <integer>
<integer> ::= <digit> | <digit> <integer>
<digit> ::= 0|1|2|3|4|5|6|7|8|9
<identifier_token> ::= <id_character> <identifier_token> | <id_character>
<id_character> ::= any character in [a-zA-Z0-9_]

<boolean_op> ::= OR | AND
<reational_op> ::= < | > | <> | = | <= | >=
<add_sub_op> ::= + | -
<mul_div_op> ::= * | / | %
<datatype> ::= INTEGER | SINGLE | DOUBLE | BOOLEAN | STRING
```