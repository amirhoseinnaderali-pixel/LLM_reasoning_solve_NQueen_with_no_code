from dataclasses import dataclass
from typing import Sequence

@dataclass(frozen=True)
class VerificationResult:
    valid: bool
    conflicts: int
    errors: tuple[str, ...]

def count_conflicts(state: Sequence[int]) -> int:
    conflicts = 0
    for i in range(len(state)):
        for j in range(i + 1, len(state)):
            if state[i] == state[j] or abs(state[i] - state[j]) == abs(i - j):
                conflicts += 1
    return conflicts

def verify_state(state: Sequence[int], n: int) -> VerificationResult:
    errors: list[str] = []
    if len(state) != n:
        errors.append(f"length {len(state)} != n {n}")
    if any(not isinstance(value, int) for value in state):
        errors.append("state contains a non-integer value")
        return VerificationResult(False, 0, tuple(errors))
    if any(value < 0 or value >= n for value in state):
        errors.append("state contains a value outside [0, n-1]")
    if len(state) == n and sorted(state) != list(range(n)):
        errors.append("state is not a permutation of 0..n-1")
    conflicts = count_conflicts(state)
    if conflicts != 0:
        errors.append(f"independent verifier counted {conflicts} conflicts")
    return VerificationResult(not errors, conflicts, tuple(errors))
