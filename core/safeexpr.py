from __future__ import annotations
import ast
from typing import Any, Dict


ALLOWED_NODES = (
    ast.Expression,
    ast.BoolOp,
    ast.BinOp,
    ast.UnaryOp,
    ast.Compare,
    ast.Name,
    ast.Load,
    ast.Constant,
    ast.And,
    ast.Or,
    ast.Not,
    ast.Eq,
    ast.NotEq,
    ast.Lt,
    ast.LtE,
    ast.Gt,
    ast.GtE,
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.Mod,
)


def safe_eval_expr(expr: str, env: Dict[str, Any]) -> Any:
    """
    Evaluate a simple expression string in a restricted environment.

    Examples:
      "TAL > LIMIT"
      "PAL_INTEGRITY == True and TAL >= 0.5"
    """
    expr = expr.strip()
    tree = ast.parse(expr, mode="eval")

    for node in ast.walk(tree):
        if not isinstance(node, ALLOWED_NODES):
            raise ValueError(f"Disallowed expression node: {type(node).__name__}")

    code = compile(tree, "<enochian-expr>", "eval")
    return eval(code, {"__builtins__": {}}, env)
