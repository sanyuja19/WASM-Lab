MINILANG_GRAMMAR = r"""
?start: program

program: function_def*

function_def: "fn" CNAME "(" [param_list] ")" "->" type_name block

param_list: param ("," param)*
param: CNAME ":" type_name

type_name: "i32" -> type_i32
         | "bool" -> type_bool

block: "{" statement* "}"

statement: var_decl
         | assign_stmt
         | if_stmt
         | while_stmt
         | return_stmt
         | expr_stmt
         | block

var_decl: "let" CNAME ":" type_name "=" expr ";"
assign_stmt: CNAME "=" expr ";"
if_stmt: "if" expr block ["else" (block | if_stmt)]
while_stmt: "while" expr block
return_stmt: "return" [expr] ";"
expr_stmt: expr ";"

?expr: logical_or

?logical_or: logical_and
           | logical_or "||" logical_and -> or_op

?logical_and: equality
            | logical_and "&&" equality -> and_op

?equality: comparison
         | equality EQ_OP comparison -> binary_op

?comparison: sum
           | comparison REL_OP sum -> binary_op

?sum: product
    | sum ADD_OP product -> binary_op

?product: unary
        | product MUL_OP unary -> binary_op

?unary: "-" unary -> neg
      | "!" unary -> not_op
      | primary

?primary: INT -> int_lit
        | "true" -> true_lit
        | "false" -> false_lit
        | CNAME "(" [arg_list] ")" -> call_expr
        | CNAME -> var_ref
        | "(" expr ")"

arg_list: expr ("," expr)*

EQ_OP: "==" | "!="
REL_OP: "<=" | ">=" | "<" | ">"
ADD_OP: "+" | "-"
MUL_OP: "*" | "/" | "%"

COMMENT: "//" /[^\n]/*
%import common.CNAME
%import common.INT
%import common.WS
%ignore WS
%ignore COMMENT
"""
