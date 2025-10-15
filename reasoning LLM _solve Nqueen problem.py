from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate


llm = ChatOllama(model="llama3.2:1b")

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


prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        (
            "You are a specialist assistant for solving the n-Queens problem. "
            "Produce only plain text lines that follow exactly the format described below. Do NOT add any extra explanation, commentary, punctuation, or blank lines.\n\n"

            "OUTPUT FORMAT (exact):\n"
            "Initial state for n={n}: [q0, q1, ...], Conflicts: C0\n"
            "Step 1: State after swap: [ ... ], Conflicts: C1\n"
            "Step 2: State after swap: [ ... ], Conflicts: C2\n"
            "...\n"
            "Final state for n={n}: [ ... ], Conflicts: 0\n\n"

            "DEFINITIONS & RULES (must be followed exactly):\n"
            "1) State representation: state is a list of length n where index = column (0..n-1) and state[i] = row (0..n-1). Example: [1,3,0,2].\n"
            "2) Conflict counting: For a given state, Conflicts = number of unordered pairs (i,j) with 0 <= i < j < n that satisfy ANY of:\n"
            "   - row conflict: state[i] == state[j]\n"
            "   - diagonal conflict: abs(state[i] - state[j]) == abs(i - j)\n"
            "   (Count each conflicting pair exactly once.)\n"
            "3) Allowed move (swap): A 'swap' exchanges the row values of two distinct columns i and j (i != j). After the swap compute new Conflicts.\n"
            "4) Move selection heuristic (deterministic): At each step, consider ALL possible swaps (i<j). Select the swap that yields the largest reduction in Conflicts (current_conflicts - new_conflicts). If multiple swaps give the same reduction, pick the swap with smallest i; if still tied, pick smallest j. If no swap reduces Conflicts, you may still output further steps up to {max_steps} but MUST follow the same deterministic tie-break rules and may stop early only when Conflicts == 0 or when step count reaches {max_steps}.\n"
            "5) Step numbering: Number steps starting from 1, increment by 1 each reported swap. Each Step line must show the full state after that swap and the resulting Conflicts.\n"
            "6) Initial state: Use exactly one 'Initial state' line showing the starting state and its Conflicts before any swaps.\n"
            "7) Final state: When you reach Conflicts == 0, print a 'Final state for n={n}: [...], Conflicts: 0' line. If you reach {max_steps} without Conflicts==0, print the last state as 'Final state for n={n}: [...], Conflicts: X' where X is the final conflict count (but prefer to reach 0 if possible).\n"
            "8) Determinism: All choices must be deterministic given the current state (no randomness).\n"
            "9) Strict formatting: Brackets, commas and spacing must match examples: comma+space between elements, no trailing commas. Each output line must be exactly one of the allowed lines above.\n\n"

            "Follow the examples in the human message for style and exact punctuation. Output only the state lines exactly as specified."
        ),
    ),
    (
        "human",
        (
            "For guidance, study the examples below and mimic the same style:\n\n{examples}"
        ),
    ),
    (
        "human",
        (
            "Now, for n={n}, produce output in the same format. If needed, do not exceed {max_steps} steps."
        ),
    ),
    (
        "human",
        (
            "If there is a previous output to refine, consider it here and improve consistency:\n{previous}"
        ),
    ),
])



def generate_n_queens_trace(n, max_steps, previous):
    """Generate a step-by-step trace for the n-Queens problem in a fixed format."""
    chain = prompt | llm
    return chain.invoke({
        "n": 20,
        "max_steps": 20,
        "examples": EXAMPLES,
        "previous": previous or "",
    })


if __name__ == "__main__":
    response1 = generate_n_queens_trace(n=20, max_steps=30, previous="")
    response2 = generate_n_queens_trace(n=20, max_steps=30, previous=response1.content)

    print(response2)