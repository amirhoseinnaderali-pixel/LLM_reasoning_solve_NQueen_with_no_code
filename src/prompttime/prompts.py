import hashlib
import json

PROMPT_VERSION = "EXP-001-PROMPT-v1"

SYSTEM_PROMPT = """You are solving one fixed N-Queens task by prompt-time self-refinement.
Return ONLY plain-text trace lines in the exact format specified below.

State representation:
- state is a permutation of 0..n-1
- index i is a column and state[i] is the row
- conflicts are unordered pairs (i,j), i<j, where either state[i] == state[j] or
  abs(state[i]-state[j]) == abs(i-j)
- each conflicting pair is counted exactly once

Trace format:
Initial state for n=N: [q0, q1, ...], Conflicts: C0
Step 1: State after swap: [q0, q1, ...], Conflicts: C1
...
Final state for n=N: [q0, q1, ...], Conflicts: C

Rules:
1. Every Step must exchange exactly two distinct positions from the previous state.
2. The state after the swap must be the exact result of that swap.
3. At each step choose the swap with the largest conflict reduction.
4. Break equal reductions by smallest first index i, then smallest second index j.
5. Stop only at a zero-conflict state or after the supplied step budget.
6. Report a complete replacement trace, not a commentary or explanation.
7. Do not invent evaluator feedback. You receive only the task and, after round 1,
   the previous model output.
"""

USER_TEMPLATE = """Frozen task:
n = {n}
initial_state = {initial_state}
max_steps = {max_steps}

{previous_instruction}
"""

PROMPT_SHA256 = hashlib.sha256(
    (PROMPT_VERSION + "\n" + SYSTEM_PROMPT + "\n" + USER_TEMPLATE).encode("utf-8")
).hexdigest()

def build_messages(*, n: int, initial_state: list[int], max_steps: int, previous: str) -> tuple[str, str]:
    if previous:
        previous_instruction = (
            "Previous model output follows. Inspect it, correct any mistakes, and return "
            "a complete replacement trace. Do not mention the editing process.\n\n"
            "PREVIOUS OUTPUT:\n" + previous
        )
    else:
        previous_instruction = "There is no previous output. Produce the initial trace from the frozen task."
    user_prompt = USER_TEMPLATE.format(
        n=n,
        initial_state=json.dumps(initial_state, separators=(",", ":")),
        max_steps=max_steps,
        previous_instruction=previous_instruction,
    )
    return SYSTEM_PROMPT, user_prompt
