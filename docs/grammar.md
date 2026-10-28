# MiniLang Formal Grammar Specification

## 1. Overview

MiniLang is a statically typed, C-family imperative programming language designed as the source frontend for the WASM Lab compiler framework. The grammar is defined in Extended Backus-Naur Form (EBNF) and parsed using an LALR(1) parser generated via Lark.

## 2. EBNF Grammar

```ebnf
Program         ::= FunctionDef*

FunctionDef     ::= "fn" Identifier "(" [ ParamList ] ")" "->" Type Block
ParamList       ::= Param ( "," Param )*
Param           ::= Identifier ":" Type

Type            ::= "i32" | "bool"

Block           ::= "{" Statement* "}"

Statement       ::= VarDecl
                  | AssignStmt
                  | IfStmt
                  | WhileStmt
                  | ReturnStmt
                  | ExprStmt
                  | Block

VarDecl         ::= "let" Identifier ":" Type "=" Expr ";"
AssignStmt      ::= Identifier "=" Expr ";"
IfStmt          ::= "if" Expr Block [ "else" ( Block | IfStmt ) ]
WhileStmt       ::= "while" Expr Block
ReturnStmt      ::= "return" [ Expr ] ";"
ExprStmt        ::= Expr ";"

Expr            ::= LogicalOr
LogicalOr       ::= LogicalAnd ( "||" LogicalAnd )*
LogicalAnd      ::= Equality ( "&&" Equality )*
Equality        ::= Comparison ( ( "==" | "!=" ) Comparison )*
Comparison      ::= Sum ( ( "<=" | ">=" | "<" | ">" ) Sum )*
Sum             ::= Product ( ( "+" | "-" ) Product )*
Product         ::= Unary ( ( "*" | "/" | "%" ) Unary )*
Unary           ::= "-" Unary | "!" Unary | Primary

Primary         ::= IntegerLiteral
                  | "true"
                  | "false"
                  | Identifier "(" [ ArgList ] ")"
                  | Identifier
                  | "(" Expr ")"

ArgList         ::= Expr ( "," Expr )*
```

## 3. Operator Precedence and Associativity

| Precedence (High to Low) | Operators | Description | Associativity |
|---|---|---|---|
| 1 (Highest) | `()`, function call | Grouping and invocation | Left-to-right |
| 2 | `-`, `!` | Unary negation, logical NOT | Right-to-left |
| 3 | `*`, `/`, `%` | Multiplication, division, remainder | Left-to-right |
| 4 | `+`, `-` | Addition, subtraction | Left-to-right |
| 5 | `<`, `<=`, `>`, `>=` | Relational comparisons | Left-to-right |
| 6 | `==`, `!=` | Equality / inequality | Left-to-right |
| 7 | `&&` | Logical AND | Left-to-right |
| 8 (Lowest) | `\|\|` | Logical OR | Left-to-right |

## 4. Lexical Rules

- **Keywords**: `fn`, `let`, `if`, `else`, `while`, `return`, `true`, `false`, `i32`, `bool`
- **Identifiers**: `[a-zA-Z_][a-zA-Z0-9_]*`
- **Integer Literals**: Decimal integers `[0-9]+`
- **Comments**: Single-line comments starting with `//` to the end of the line
- **Whitespace**: Space, tabs, and newlines are ignored outside tokens
