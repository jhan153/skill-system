#!/usr/bin/env python3
"""Sample a stated z=f(x,y) into Report Canvas buffer_geometry.

This authors display data for spatial reports. It does not implement a
production topology algorithm or evaluate arbitrary Python.
"""
from __future__ import annotations

import argparse
import ast
import json
import math
from pathlib import Path
from typing import Any, Callable


ALLOWED_FUNCS: dict[str, Callable[..., float]] = {
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "asin": math.asin,
    "acos": math.acos,
    "atan": math.atan,
    "atan2": math.atan2,
    "sinh": math.sinh,
    "cosh": math.cosh,
    "tanh": math.tanh,
    "exp": math.exp,
    "sqrt": math.sqrt,
    "log": math.log,
    "log10": math.log10,
    "abs": abs,
    "fabs": math.fabs,
    "floor": math.floor,
    "ceil": math.ceil,
    "hypot": math.hypot,
    "pow": pow,
    "min": min,
    "max": max,
}
ALLOWED_CONSTS = {"pi": math.pi, "e": math.e, "tau": math.tau}


class UnsafeExpression(ValueError):
    """Raised when an expression uses a name or node outside the allowlist."""


class _SafeEvaluator(ast.NodeVisitor):
    def __init__(self, names: dict[str, float]) -> None:
        self.names = names

    def visit(self, node: ast.AST) -> Any:
        method = getattr(self, f"visit_{type(node).__name__}", None)
        if method is None:
            raise UnsafeExpression(f"disallowed expression node: {type(node).__name__}")
        return method(node)

    def visit_Expression(self, node: ast.Expression) -> float:
        return float(self.visit(node.body))

    def visit_Constant(self, node: ast.Constant) -> float:
        if isinstance(node.value, bool) or not isinstance(node.value, (int, float)):
            raise UnsafeExpression("only numeric constants are allowed")
        return float(node.value)

    def visit_Name(self, node: ast.Name) -> float:
        if node.id in self.names:
            return float(self.names[node.id])
        if node.id in ALLOWED_CONSTS:
            return float(ALLOWED_CONSTS[node.id])
        if node.id in ALLOWED_FUNCS:
            raise UnsafeExpression(f"function {node.id} must be called")
        raise UnsafeExpression(f"unknown name: {node.id}")

    def visit_UnaryOp(self, node: ast.UnaryOp) -> float:
        operand = self.visit(node.operand)
        if isinstance(node.op, ast.UAdd):
            return +operand
        if isinstance(node.op, ast.USub):
            return -operand
        raise UnsafeExpression("disallowed unary operator")

    def visit_BinOp(self, node: ast.BinOp) -> float:
        left = self.visit(node.left)
        right = self.visit(node.right)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Div):
            return left / right
        if isinstance(node.op, ast.Pow):
            return left**right
        if isinstance(node.op, ast.Mod):
            return left % right
        raise UnsafeExpression("disallowed binary operator")

    def visit_Call(self, node: ast.Call) -> float:
        if node.keywords:
            raise UnsafeExpression("keyword arguments are not allowed")
        if not isinstance(node.func, ast.Name) or node.func.id not in ALLOWED_FUNCS:
            raise UnsafeExpression("only allowlisted functions may be called")
        args = [self.visit(arg) for arg in node.args]
        return float(ALLOWED_FUNCS[node.func.id](*args))


def compile_expression(expr: str) -> ast.Expression:
    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError as exc:
        raise UnsafeExpression(f"invalid expression: {exc.msg}") from exc
    _SafeEvaluator({"x": 0.0, "y": 0.0}).visit(tree)
    return tree


def evaluate(tree: ast.Expression, x: float, y: float) -> float:
    return float(_SafeEvaluator({"x": x, "y": y}).visit(tree))


def sample_surface(
    expr: str,
    *,
    xmin: float,
    xmax: float,
    ymin: float,
    ymax: float,
    nx: int,
    ny: int,
) -> dict[str, Any]:
    if nx < 2 or ny < 2:
        raise ValueError("nx and ny must be at least 2")
    if xmin >= xmax or ymin >= ymax:
        raise ValueError("axis bounds must be increasing")
    tree = compile_expression(expr)
    positions: list[float] = []
    for j in range(ny):
        y = ymin + (ymax - ymin) * j / (ny - 1)
        for i in range(nx):
            x = xmin + (xmax - xmin) * i / (nx - 1)
            z = evaluate(tree, x, y)
            if not math.isfinite(z):
                raise ValueError(f"non-finite z at x={x}, y={y}")
            positions.extend((x, z, y))
    indices: list[int] = []
    for j in range(ny - 1):
        for i in range(nx - 1):
            a = j * nx + i
            b = a + 1
            c = a + nx
            d = c + 1
            indices.extend((a, c, b, b, c, d))
    return {
        "format": "buffer_geometry",
        "geometry": {
            "positions": positions,
            "indices": indices,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expr", required=True, help="z = f(x, y) using the math allowlist")
    parser.add_argument("--xmin", type=float, default=-1.0)
    parser.add_argument("--xmax", type=float, default=1.0)
    parser.add_argument("--ymin", type=float, default=-1.0)
    parser.add_argument("--ymax", type=float, default=1.0)
    parser.add_argument("--nx", type=int, default=24)
    parser.add_argument("--ny", type=int, default=24)
    parser.add_argument("--out", required=True, help="geometry JSON output path")
    args = parser.parse_args(argv)
    payload = sample_surface(
        args.expr,
        xmin=args.xmin,
        xmax=args.xmax,
        ymin=args.ymin,
        ymax=args.ymax,
        nx=args.nx,
        ny=args.ny,
    )
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
