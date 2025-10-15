## PromptTime-Search: N-Queens Reasoner

A tiny, iterative prompting loop that turns a small local model into a step-by-step searcher at prompt time. It re-feeds the previous response to refine the next one, demonstrating test-time scaling of reasoning without changing weights.

### What this repo shows
- **Prompt-time scaling**: Better reasoning by looping the model with its own previous output as context.
- **Deterministic search prompt**: A strict output format and greedy swap heuristic for n-Queens.
- **Few-shot + refinement**: A small model + examples + iterative self-refinement yields visible search behavior.

---

### Requirements
- Python 3.9+
- [Ollama](https://ollama.com) installed and running
- Pull a small model (default used here):

```bash
ollama pull llama3.2:1b
```

- Python deps:

```bash
pip install langchain-ollama langchain-core
```

### Run

```bash
python o9.py
```

You should see a multi-line trace like:

```text
Initial state for n=20: [...], Conflicts: C0
Step 1: State after swap: [...], Conflicts: C1
...
Final state for n=20: [...], Conflicts: 0
```

### How it works
- The prompt defines a strict format and a deterministic greedy move policy (swap columns that most reduce conflicts; tie-break by smallest i then j).
- `o9.py` runs the chain twice: the second call receives the first output under `previous`, nudging the model to continue/refine the same trajectory.
- This loop can be extended to more than two rounds to further stabilize/improve results.

### Iterating more rounds
Minimal sketch to extend the loop:

```python
from o9 import generate_n_queens_trace

previous = ""
for _ in range(5):
    res = generate_n_queens_trace(n=20, max_steps=30, previous=previous)
    previous = res.content
print(previous)
```

### Tuning knobs
- **Model**: change `model="llama3.2:1b"` in `o9.py` to any local Ollama model you prefer.
- **Problem size**: switch `n` to larger values to stress test search behavior.
- **Budget**: change `max_steps` to allow longer traces.
- **Examples**: enrich `EXAMPLES` to guide formatting and behavior.

### Note about current script
In `generate_n_queens_trace`, the `n` and `max_steps` arguments are currently hard-coded to `20` in the payload. If you want the function parameters to take effect, replace those with the function arguments.

### Why n-Queens?
It’s discrete, structured, and admits a verifiable, non-ambiguous trace. That makes prompt-time refinement clearly visible and easy to evaluate.

### License
MIT


