# Reproducibility

Requirements:

- Ollama
- `llama3.2:1b`
- Python 3.9+
- langchain-ollama
- langchain-core

Run the prototype:

```bash
python "reasoning LLM _solve Nqueen problem.py" --n 20 --max-steps 30 --rounds 2
```

For controlled experiments use a fixed model and temperature 0.

Every experiment should record model name, n, max_steps, rounds, seed if relevant, wall-clock time, and final independently verified state.
