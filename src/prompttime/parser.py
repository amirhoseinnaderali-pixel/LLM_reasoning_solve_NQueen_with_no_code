from dataclasses import dataclass
import re
from .verifier import VerificationResult, verify_state

_INITIAL_RE = re.compile(r"^Initial state for n=(?P<n>\d+): \[(?P<state>[^\]]*)\], Conflicts: (?P<conflicts>\d+)$")
_STEP_RE = re.compile(r"^Step (?P<step>\d+): State after swap: \[(?P<state>[^\]]*)\], Conflicts: (?P<conflicts>\d+)$")
_FINAL_RE = re.compile(r"^Final state for n=(?P<n>\d+): \[(?P<state>[^\]]*)\], Conflicts: (?P<conflicts>\d+)$")

@dataclass(frozen=True)
class ParsedLine:
    number: int
    state: list[int]
    reported_conflicts: int
    kind: str

@dataclass(frozen=True)
class ParsedTrace:
    initial: ParsedLine
    steps: tuple[ParsedLine, ...]
    final: ParsedLine

@dataclass(frozen=True)
class TraceValidation:
    valid: bool
    initial_conflicts: int | None
    final_state: list[int] | None
    final_conflicts: int | None
    errors: tuple[str, ...]
    state_results: tuple[VerificationResult, ...]

class TraceParseError(ValueError):
    pass

def _parse_state(text: str) -> list[int]:
    if not text.strip():
        return []
    try:
        return [int(part.strip()) for part in text.split(",")]
    except ValueError as exc:
        raise TraceParseError("state contains a non-integer token") from exc

def parse_trace(text: str) -> ParsedTrace:
    if not isinstance(text, str) or not text.strip():
        raise TraceParseError("empty model output")
    lines = text.splitlines()
    if any(not line.strip() for line in lines):
        raise TraceParseError("blank lines are not allowed")
    initial_match = _INITIAL_RE.match(lines[0])
    if not initial_match:
        raise TraceParseError("first line is not an Initial state line")
    initial = ParsedLine(0, _parse_state(initial_match.group("state")),
                         int(initial_match.group("conflicts")), "initial")
    steps: list[ParsedLine] = []
    index, expected_step = 1, 1
    while index < len(lines) and lines[index].startswith("Step "):
        match = _STEP_RE.match(lines[index])
        if not match:
            raise TraceParseError(f"malformed step line at line {index + 1}")
        step_number = int(match.group("step"))
        if step_number != expected_step:
            raise TraceParseError(f"step numbering is not sequential: expected {expected_step}, got {step_number}")
        steps.append(ParsedLine(step_number, _parse_state(match.group("state")),
                                int(match.group("conflicts")), "step"))
        expected_step += 1
        index += 1
    if index >= len(lines):
        raise TraceParseError("final state line is missing")
    final_match = _FINAL_RE.match(lines[index])
    if not final_match:
        raise TraceParseError(f"malformed final line at line {index + 1}")
    final = ParsedLine(0, _parse_state(final_match.group("state")),
                       int(final_match.group("conflicts")), "final")
    if index != len(lines) - 1:
        raise TraceParseError("unexpected content after final state")
    return ParsedTrace(initial=initial, steps=tuple(steps), final=final)

def _swap_transition(previous: list[int], current: list[int]) -> tuple[bool, str]:
    if len(previous) != len(current):
        return False, "state lengths changed across a transition"
    changed = [i for i, (a, b) in enumerate(zip(previous, current)) if a != b]
    if len(changed) != 2:
        return False, f"expected exactly two changed positions, found {len(changed)}"
    i, j = changed
    if current[i] != previous[j] or current[j] != previous[i]:
        return False, f"positions {i} and {j} do not form an exact swap"
    return True, ""

def validate_trace(trace: ParsedTrace, *, n: int, expected_initial_state: list[int], max_steps: int) -> TraceValidation:
    errors: list[str] = []
    state_results: list[VerificationResult] = []
    if trace.initial.state != expected_initial_state:
        errors.append("model initial state does not match the frozen benchmark task")
    initial_result = verify_state(trace.initial.state, n)
    state_results.append(initial_result)
    if trace.initial.reported_conflicts != initial_result.conflicts:
        errors.append("initial reported conflict count does not match the independent verifier")
    if len(trace.steps) > max_steps:
        errors.append(f"step count {len(trace.steps)} exceeds max_steps {max_steps}")
    previous = trace.initial.state
    for expected_step, step in enumerate(trace.steps, start=1):
        if step.number != expected_step:
            errors.append(f"step number {step.number} is not {expected_step}")
        ok, reason = _swap_transition(previous, step.state)
        if not ok:
            errors.append(f"step {expected_step}: {reason}")
        result = verify_state(step.state, n)
        state_results.append(result)
        if step.reported_conflicts != result.conflicts:
            errors.append(f"step {expected_step}: reported conflicts {step.reported_conflicts} != verified {result.conflicts}")
        previous = step.state
    final_result = verify_state(trace.final.state, n)
    state_results.append(final_result)
    if trace.final.state != previous:
        errors.append("final state does not equal the last step state")
    if trace.final.reported_conflicts != final_result.conflicts:
        errors.append(f"final reported conflicts {trace.final.reported_conflicts} != verified {final_result.conflicts}")
    return TraceValidation(
        valid=not errors,
        initial_conflicts=initial_result.conflicts,
        final_state=list(trace.final.state),
        final_conflicts=final_result.conflicts,
        errors=tuple(errors),
        state_results=tuple(state_results),
    )

def parse_and_validate(text: str, *, n: int, expected_initial_state: list[int], max_steps: int) -> TraceValidation:
    try:
        parsed = parse_trace(text)
    except TraceParseError as exc:
        return TraceValidation(False, None, None, None, (str(exc),), ())
    return validate_trace(parsed, n=n, expected_initial_state=expected_initial_state, max_steps=max_steps)
