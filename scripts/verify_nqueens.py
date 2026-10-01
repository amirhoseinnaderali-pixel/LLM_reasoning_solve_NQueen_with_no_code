import argparse
import ast
import json
import re
from itertools import combinations


def count_conflicts(state):
    n = len(state)
    conflicts = 0
    for i, j in combinations(range(n), 2):
        if state[i] == state[j] or abs(state[i] - state[j]) == abs(i - j):
            conflicts += 1
    return conflicts


def parse_final_state(text):
    match = re.search(r"Final state for n=(\d+):\s*(\[[^\n]+\])\s*,\s*Conflicts:\s*(\d+)", text)
    if not match:
        return None
    n = int(match.group(1))
    try:
        state = ast.literal_eval(match.group(2))
    except (SyntaxError, ValueError):
        return None
    if not isinstance(state, list):
        return None
    return n, state


def verify(text):
    parsed = parse_final_state(text)
    if parsed is None:
        return {"parseable": False}
    n, state = parsed
    valid_permutation = len(state) == n and sorted(state) == list(range(n))
    true_conflicts = count_conflicts(state) if valid_permutation else None
    return {
        "parseable": True,
        "n": n,
        "valid_permutation": valid_permutation,
        "true_conflicts": true_conflicts,
        "success": valid_permutation and true_conflicts == 0,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Text file containing a model trace")
    args = parser.parse_args()
    text = open(args.file, encoding="utf-8").read()
    print(json.dumps(verify(text), indent=2))


if __name__ == "__main__":
    main()
