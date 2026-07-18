from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import re

from .tables import Table, Sigillum, CellAddress
from .safeexpr import safe_eval_expr


class Watchtower(Enum):
    EAST = "EAST"   # Air: logic, inference
    WEST = "WEST"   # Water: memory, affect
    NORTH = "NORTH" # Earth: structure, ontology
    SOUTH = "SOUTH" # Fire: action, transformation


@dataclass
class Aethyr:
    number: int  # 1..30
    name: Optional[str] = None

    def __post_init__(self):
        if not (1 <= self.number <= 30):
            raise ValueError("Aethyr number must be between 1 and 30.")


@dataclass
class Context:
    watchtower: Watchtower
    aethyr: Aethyr
    bindings: Dict[str, Any] = field(default_factory=dict)


class Opcode(Enum):
    UN = auto()     # assert
    PA = auto()     # open
    VEH = auto()    # transition
    GRAPH = auto()  # bind
    NA = auto()     # negate
    TAL = auto()    # measure
    DRUX = auto()   # divide
    MED = auto()    # merge
    GON = auto()    # generate
    FAM = auto()    # focus
    VAN = auto()    # expand
    PAL = auto()    # protect
    UR = auto()     # recall
    CEPH = auto()   # store
    LUX = auto()    # illuminate
    ZOD = auto()    # index
    IAL = auto()    # loop
    MOS = auto()    # halt
    ROX = auto()    # route
    SIG = auto()    # sign
    EL = auto()     # elevate


@dataclass
class Instruction:
    opcode: Opcode
    target: Optional[str] = None
    context: Optional[str] = None
    condition: Optional[str] = None
    block: Optional[List["Statement"]] = None


@dataclass
class IfStatement:
    condition: str
    then_block: List[Statement]
    else_block: Optional[List[Statement]] = None


@dataclass
class LoopStatement:
    condition: str
    block: List[Statement]


@dataclass
class CallStatement:
    name: str
    block: List[Statement]


Statement = Union[Instruction, IfStatement, LoopStatement, CallStatement]


@dataclass
class Program:
    statements: List[Statement]


@dataclass
class Event:
    """
    Structured event for logging and archetype detection.
    """
    opcode: str
    target: Optional[str]
    watchtower: str
    aethyr: int
    payload: Dict[str, Any] = field(default_factory=dict)


# ---------- Correct regexes ----------

CALL_RE = re.compile(r"CALL_(\w+)\s*{")
IF_RE   = re.compile(r"IF\s+(.+?)\s*{")
IAL_RE  = re.compile(r"IAL(?:\s+UNTIL\s+(.+?))?\s*{")
OPCODE_RE = re.compile(r"^([A-Z]+)\b")


def _parse_opcode(token: str) -> Opcode:
    token = token.upper()
    try:
        return Opcode[token]
    except KeyError:
        raise ValueError(f"Unknown opcode: {token}")


class EnochianInterpreter:
    """
    Interpreter for the Enochian DSL (v0.1).

    Maintains:
      - context_stack: List[Context]
      - tables: Dict[str, Table]
      - sigillum: Sigillum
      - variables: Dict[str, Any]
      - events: List[Event]
    """

    def __init__(self, tables: Optional[Dict[str, Table]] = None, sigillum: Optional[Sigillum] = None):
        self.context_stack: List[Context] = []
        self.tables = tables or {}
        self.sigillum = sigillum or Sigillum()
        self.variables: Dict[str, Any] = {}
        self.events: List[Event] = []

        # Opcode handlers
        self._opcode_handlers: Dict[Opcode, Callable] = {
            op: getattr(self, f"exec_{op.name}")
            for op in Opcode
        }

    # ---------- Context management ----------

    def push_context(self, ctx: Context):
        self.context_stack.append(ctx)

    def pop_context(self) -> Context:
        return self.context_stack.pop()

    @property
    def current_context(self) -> Context:
        if not self.context_stack:
            return Context(watchtower=Watchtower.EAST, aethyr=Aethyr(18))
        return self.context_stack[-1]

    # ---------- Execution entry ----------

    def run(self, program: Program, initial_context: Optional[Context] = None):
        if initial_context:
            self.push_context(initial_context)
        for stmt in program.statements:
            self._exec_statement(stmt)

    def _exec_statement(self, stmt: Statement):
        if isinstance(stmt, Instruction):
            self._exec_instruction(stmt)
        elif isinstance(stmt, IfStatement):
            self._exec_if(stmt)
        elif isinstance(stmt, LoopStatement):
            self._exec_loop(stmt)
        elif isinstance(stmt, CallStatement):
            self._exec_call(stmt)
        else:
            raise RuntimeError(f"Unknown statement type: {type(stmt)}")

    # ---------- Structured constructs ----------

    def _eval_condition(self, condition: str) -> bool:
        # Merge variables with context info
        env = dict(self.variables)
        ctx = self.current_context
        env.update({
            "WATCHTOWER": ctx.watchtower.value,
            "AETHYR": ctx.aethyr.number,
        })
        try:
            return bool(safe_eval_expr(condition, env))
        except Exception as e:
            self._append_event("CONDITION_ERROR", None, {"error": str(e), "condition": condition})
            return False

    def _exec_if(self, stmt: IfStatement):
        if self._eval_condition(stmt.condition):
            for b in stmt.then_block:
                self._exec_statement(b)
        elif stmt.else_block:
            for b in stmt.else_block:
                self._exec_statement(b)

    def _exec_loop(self, stmt: LoopStatement):
        max_iters = 100
        iters = 0
        while iters < max_iters and self._eval_condition(stmt.condition):
            for b in stmt.block:
                self._exec_statement(b)
            iters += 1
        if iters >= max_iters:
            self._append_event("LOOP_MAX_ITERS", None, {"condition": stmt.condition})

    def _exec_call(self, stmt: CallStatement):
        self._append_event("CALL", stmt.name, {})
        for b in stmt.block:
            self._exec_statement(b)

    # ---------- Instruction dispatch ----------

    def _exec_instruction(self, instr: Instruction):
        handler = self._opcode_handlers[instr.opcode]
        handler(instr)

    def _append_event(self, opcode: str, target: Optional[str], payload: Dict[str, Any]):
        ctx = self.current_context
        self.events.append(Event(
            opcode=opcode,
            target=target,
            watchtower=ctx.watchtower.value,
            aethyr=ctx.aethyr.number,
            payload=payload,
        ))

    # ---------- Opcode implementations (v0.1) ----------

    def exec_UN(self, instr: Instruction):
        target = instr.target or "STATE"
        self.variables[target] = True
        self._append_event("UN", target, {"value": True})

    def exec_PA(self, instr: Instruction):
        target = instr.target or "CONTEXT"
        self._append_event("PA", target, {"watchtower": self.current_context.watchtower.value})

    def exec_VEH(self, instr: Instruction):
        target = instr.target or "STATE"
        self.variables[f"{target}_TRANSITIONED"] = True
        self._append_event("VEH", target, {})

    def exec_GRAPH(self, instr: Instruction):
        target = instr.target or "RELATION"
        self.variables[f"BOUND_{target}"] = True
        self._append_event("GRAPH", target, {})

    def exec_NA(self, instr: Instruction):
        target = instr.target or "STATE"
        self.variables[target] = False
        self._append_event("NA", target, {"value": False})

    def exec_TAL(self, instr: Instruction):
        # Watchtower-specific semantics
        wt = self.current_context.watchtower
        target = instr.target or "METRIC"

        if wt == Watchtower.EAST:
            # Logic: relational density
            value = 0.65 + (hash(target) % 100) / 300.0
        elif wt == Watchtower.WEST:
            # Memory/affect: salience
            value = 0.4 + (len(target or "") % 10) / 20.0
        elif wt == Watchtower.NORTH:
            # Structure: schema fit
            value = 0.8
        else:  # SOUTH
            # Action: execution readiness
            value = 0.55

        self.variables[target] = value
        self.variables["TAL"] = value  # convenience
        self._append_event("TAL", target, {"value": value, "watchtower": wt.value})

    def exec_DRUX(self, instr: Instruction):
        target = instr.target or "SET"
        self.variables[f"{target}_DIVIDED"] = True
        self._append_event("DRUX", target, {})

    def exec_MED(self, instr: Instruction):
        target = instr.target or "STREAM"
        self.variables[f"{target}_MERGED"] = True
        self._append_event("MED", target, {})

    def exec_GON(self, instr: Instruction):
        target = instr.target or "STRUCTURE"
        self.variables[f"GENERATED_{target}"] = True
        self._append_event("GON", target, {})

    def exec_FAM(self, instr: Instruction):
        target = instr.target or "ATTENTION"
        self.variables[f"FOCUSED_{target}"] = True
        self._append_event("FAM", target, {})

    def exec_VAN(self, instr: Instruction):
        target = instr.target or "SCOPE"
        self.variables[f"EXPANDED_{target}"] = True
        self._append_event("VAN", target, {})

    def exec_PAL(self, instr: Instruction):
        target = instr.target or "INVARIANT"
        self.variables[f"PROTECTED_{target}"] = True
        self._append_event("PAL", target, {})

    def exec_UR(self, instr: Instruction):
        target = instr.target or "MEMORY"
        self.variables[f"RECALLED_{target}"] = True
        self._append_event("UR", target, {})

    def exec_CEPH(self, instr: Instruction):
        target = instr.target or "VALUE"
        self.variables[f"STORED_{target}"] = True
        self._append_event("CEPH", target, {})

    def exec_LUX(self, instr: Instruction):
        target = instr.target or "RELATIONS"
        self.variables[f"ILLUMINATED_{target}"] = True
        self._append_event("LUX", target, {})

    def exec_ZOD(self, instr: Instruction):
        target = instr.target or "TABLE"
        # Future: parse TABLE_ALPHA[3,7] and use parse_address()
        self.variables[f"INDEXED_{target}"] = True
        self._append_event("ZOD", target, {})

    def exec_IAL(self, instr: Instruction):
        target = instr.target or "PROCESS"
        self.variables[f"LOOPING_{target}"] = True
        self._append_event("IAL", target, {})

    def exec_MOS(self, instr: Instruction):
        if len(self.context_stack) > 1:
            closed = self.pop_context()
            self._append_event("MOS", None, {
                "sealed_aethyr": closed.aethyr.number,
                "sealed_watchtower": closed.watchtower.value,
            })
        else:
            self._append_event("MOS", None, {"sealed_process": True})

    def exec_ROX(self, instr: Instruction):
        target = instr.target or "SIGNAL"
        self.variables[f"ROUTED_{target}"] = True
        self._append_event("ROX", target, {})

    def exec_SIG(self, instr: Instruction):
        target = instr.target or "ENTITY"
        self.variables[f"SIGNED_{target}"] = True
        self._append_event("SIG", target, {})

    def exec_EL(self, instr: Instruction):
        ctx = self.current_context

        if instr.target and instr.target.upper().startswith("AETHYR_"):
            # Parse explicit target like AETHYR_25
            try:
                new_num = int(instr.target.split("_", 1)[1])
                new_num = max(1, min(30, new_num))
            except (ValueError, IndexError):
                new_num = min(30, ctx.aethyr.number + 1)
        else:
            new_num = min(30, ctx.aethyr.number + 1)

        new_ctx = Context(
            watchtower=ctx.watchtower,
            aethyr=Aethyr(new_num),
            bindings=dict(ctx.bindings),
        )
        self.push_context(new_ctx)
        self._append_event("EL", instr.target, {
            "from_aethyr": ctx.aethyr.number,
            "to_aethyr": new_num,
            "watchtower": ctx.watchtower.value,
        })


# ---------- Parser (v0.1) ----------

def parse_program(source: str) -> Program:
    """
    Parser for the Enochian DSL (v0.1).

    Supports:
      - OPCODE [TARGET] [CONTEXT] [IF COND]
      - IF COND { ... } ELSE { ... }
      - IAL [UNTIL COND] { ... }
      - CALL_name { ... }
    """
    lines = source.splitlines()
    statements: List[Statement] = []
    i = 0

    while i < len(lines):
        line = lines[i].strip()
        if not line or line.startswith("#"):
            i += 1
            continue

        # CALL_name {
        m = CALL_RE.match(line)
        if m:
            name = m.group(1)
            block_lines, i = _extract_block(lines, i + 1)
            block = parse_program("\n".join(block_lines)).statements
            statements.append(CallStatement(name=f"CALL_{name}", block=block))
            continue

        # IF COND {
        m = IF_RE.match(line)
        if m:
            cond = m.group(1).strip()
            then_lines, i = _extract_block(lines, i + 1)
            then_block = parse_program("\n".join(then_lines)).statements

            else_block = None
            # Robust ELSE handling: skip whitespace/comments, then check next non-empty line
            while i < len(lines):
                peek = lines[i].strip()
                if not peek or peek.startswith("#"):
                    i += 1
                    continue
                if peek.startswith("ELSE"):
                    else_lines, i = _extract_block(lines, i + 1)
                    else_block = parse_program("\n".join(else_lines)).statements
                break

            statements.append(IfStatement(condition=cond, then_block=then_block, else_block=else_block))
            continue

        # IAL [UNTIL COND] {
        m = IAL_RE.match(line)
        if m:
            cond = (m.group(1) or "True").strip()
            block_lines, i = _extract_block(lines, i + 1)
            block = parse_program("\n".join(block_lines)).statements
            statements.append(LoopStatement(condition=cond, block=block))
            continue

        # OPCODE ...
        m = OPCODE_RE.match(line)
        if not m:
            i += 1
            continue

        opcode = _parse_opcode(m.group(1))
        rest = line[m.end():].strip()
        parts = rest.split()
        target = parts[0] if len(parts) > 0 else None
        context = parts[1] if len(parts) > 1 else None
        condition = None
        if "IF" in parts:
            idx = parts.index("IF")
            condition = " ".join(parts[idx + 1 :])

        statements.append(Instruction(opcode=opcode, target=target, context=context, condition=condition))
        i += 1

    return Program(statements=statements)


def _extract_block(lines: List[str], start_idx: int) -> Tuple[List[str], int]:
    """
    Extract a brace-delimited block starting after the opening '{'.

    Returns (block_lines, end_index) where end_index is the line after the closing '}'.
    """
    block_lines = []
    depth = 0
    i = start_idx

    while i < len(lines):
        line = lines[i]
        depth += line.count("{")
        depth -= line.count("}")

        # Handle content after opening brace on the same line
        if "{" in line and depth > 0:
            after = line.split("{", 1)[1]
            if after.strip():
                # If closing brace also on this line, strip it
                if "}" in after:
                    after = after.rsplit("}", 1)[0]
                block_lines.append(after)
        elif "}" not in line:
            block_lines.append(line)

        if depth <= 0:
            break
        i += 1

    if depth != 0:
        raise SyntaxError("Unbalanced braces in block")

    return block_lines, i + 1
