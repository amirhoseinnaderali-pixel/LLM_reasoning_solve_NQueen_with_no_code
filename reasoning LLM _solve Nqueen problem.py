"""Historical/demo prototype preserved for provenance.

This file is not imported by the controlled EXP-001 instrument.
The original caller-controlled parameters and configurable round count are respected here so the demo itself no longer silently ignores them.
"""

import argparse
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

EXAMPLES = """
Example 1: 4 Queens
Initial state for n=4: [1, 2, 3, 0], Conflicts: 1
Step 1: State after swap: [1, 0, 3, 2], Conflicts: 1
Step 2: State after swap: [3, 0, 1, 2], Conflicts: 1
...
Final state for n=4: [1, 3, 0, 2], Conflicts: 0
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", (
        "You are a specialist assistant for solving the n-Queens problem. "
        "Produce only plain text lines in the requested trace format.\n\n"
        "OUTPUT FORMAT (exact):\n"
        "Initial state for n={n}: [q0, q1, ...], Conflicts: C0\n"
        "Step 1: State after swap: [ ... ], Conflicts: C1\n"
        "Final state for n={n}: [ ... ], Conflicts: X\n\n"
        "State representation: index=column and state[i]=row. "
        "Conflicts are unordered pairs with a row or diagonal conflict. "
        "At each step select the swap with largest conflict reduction, then smallest i/j."
    )),
    ("human", "Examples:\n{examples}"),
    ("human", "For n={n}, do not exceed {max_steps} steps."),
    ("human", "Previous output to refine, if any:\n{previous}"),
])

def generate_n_queens_trace(n, max_steps, previous, *, model="llama3.2:1b"):
    chain = prompt | ChatOllama(model=model)
    return chain.invoke({
        "n": n,
        "max_steps": max_steps,
        "examples": EXAMPLES,
        "previous": previous or "",
    })

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=20)
    parser.add_argument("--max-steps", type=int, default=20)
    parser.add_argument("--rounds", type=int, default=2)
    parser.add_argument("--model", default="llama3.2:1b")
    args = parser.parse_args()

    previous = ""
    for _ in range(args.rounds):
        response = generate_n_queens_trace(args.n, args.max_steps, previous, model=args.model)
        previous = response.content
    print(previous)
