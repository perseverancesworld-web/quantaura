from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class CellAddress:
    table: str
    row: int
    col: int


class Table:
    def __init__(self, name: str):
        self.name = name
        self.cells: Dict[tuple[int, int], Any] = {}

    def set(self, row: int, col: int, value: Any):
        self.cells[(row, col)] = value

    def get(self, row: int, col: int) -> Any:
        return self.cells.get((row, col))


class Sigillum:
    def __init__(self):
        self.constraints: Dict[str, Any] = {}

    def bind(self, context: str, rules: Any):
        self.constraints[context] = rules

    def enforce(self, context: str) -> bool:
        return self.constraints.get(context, True)
