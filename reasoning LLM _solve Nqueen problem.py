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

Example 2: 8 Queens
Initial state for n=8: [5, 2, 7, 1, 6, 0, 4, 3], Conflicts: 3
Step 1: State after swap: [5, 2, 0, 1, 6, 7, 4, 3], Conflicts: 3
Step 2: State after swap: [5, 2, 0, 1, 3, 7, 4, 6], Conflicts: 2
.....
Final state for n=8: [4, 2, 0, 6, 1, 7, 5, 3], Conflicts: 0

Example 3: 10 Queens
Initial state for n=10: [7, 1, 8, 3, 0, 4, 9, 2, 6, 5], Conflicts: 4
Step 1: State after swap: [7, 1, 8, 3, 6, 4, 9, 2, 0, 5], Conflicts: 4
Step 2: State after swap: [7, 1, 0, 3, 6, 4, 9, 2, 8, 5], Conflicts: 3
Final state for n=10: [9, 3, 0, 4, 1, 8, 6, 2, 5, 7], Conflicts: 0
"""

PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            (
                "You are a specialist assistant for solving the n-Queens problem. "
                "Return only the specified state lines.\n\n"
                "OUTPUT FORMAT:\n"
                "Initial state for n={n}: [q0, q1, ...], Conflicts: C0\n"
                "Step 1: State after swap: [ ... ], Conflicts: C1\n"
                "Step 2: State after swap: [ ... ], Conflicts: C2\n"
                "Final state for n={n}: [ ... ], Conflicts: X\n\n"
                "RULES:\n"
                "1) State is a list of length n; state[i] is the row in column i.\n"
                "2) Conflicts count unordered pairs with equal rows or equal diagonals.\n"
                "3) A move swaps the row values of two columns.\n"
                "4) Prefer the swap with the largest conflict reduction; break ties by smallest i then j.\n"
                "5) Stop when Conflicts == 0 or at max_steps.\n"
                "6) Never add explanation outside the state lines."
            ),
        ),
        (
            "human",
            "Examples:\n\n{examples}\n\nSolve n={n} with at most {max_steps} steps.",
        ),
        (
            "human",
            "Previous trajectory to refine (empty on first round):\n{previous}",
        ),
    ]
)


def build_llm(model: str, temperature: float = 0.0) -> ChatOllama:
    return ChatOllama(model=model, temperature=temperature)


def generate_n_queens_trace(
    n: int, max_steps: int, previous: str = "", model: str = "llama3.2:1b"
):
    llm = build_llm(model)
    return (PROMPT | llm).invoke(
        {
            "n": n,
            "max_steps": max_steps,
            "examples": EXAMPLES,
            "previous": previous or "",
        }
    )


def iterative_reason(n: int, max_steps: int, rounds: int, model: str = "llama3.2:1b"):
    previous = ""
    traces = []
    for round_idx in range(rounds):
        response = generate_n_queens_trace(n, max_steps, previous, model)
        previous = response.content
        traces.append({"round": round_idx + 1, "text": previous})
    return traces


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=20)
    parser.add_argument("--max-steps", type=int, default=30)
    parser.add_argument("--rounds", type=int, default=2)
    parser.add_argument("--model", default="llama3.2:1b")
    args = parser.parse_args()

    for item in iterative_reason(args.n, args.max_steps, args.rounds, args.model):
        print(f"\n=== ROUND {item['round']} ===")
        print(item["text"])


if __name__ == "__main__":
    main()
