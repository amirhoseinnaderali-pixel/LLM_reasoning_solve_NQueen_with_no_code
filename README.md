# Prompt-Time Search: N-Queens Reasoning

This project studies **test-time compute**: improving a frozen small language model by giving it additional iterative reasoning opportunities rather than changing its weights.

## Research question

> Can iterative prompt-time refinement make a small frozen language model behave like a useful search procedure on a verifiable combinatorial problem?

## Hypothesis

> Increasing iterative inference-time computation will increase the probability that the model produces a valid N-Queens solution, at increasing latency cost.

## Prototype

The original implementation used:

- Ollama
- `llama3.2:1b`
- structured N-Queens prompting
- iterative self-refinement by feeding the previous output back to the model

The original README documented a qualitative n=20 example reaching a reported conflict count of 0.

That example is historical evidence only. A model-reported conflict count is not accepted as proof until the state is independently checked by code.

## Controlled experiment

This branch defines a benchmark over:

- n = 8, 12, 20, 30
- 1, 2, 3, and 5 refinement rounds
- fixed temperature = 0
- max 30 steps per round
- repeated trials

For every output, the verifier independently checks:

- state is parseable
- state length is n
- state is a permutation of 0..n-1
- true conflict count
- whether the final state is a valid solution

The primary analysis is **success rate vs inference budget**.

## Why this matters

Unlike a normal fine-tuning experiment, the model weights stay frozen.

The experiment therefore isolates a different form of computation allocation:

`more inference-time reasoning` instead of `more training-time parameter updates`.

This connects to the broader trajectory:

`Efficient adaptation → DPO → Distillation → Test-time compute`

## Current status

| Stage | Status |
|---|---|
| Original prototype | complete |
| Scientific audit | complete |
| Independent correctness verifier | implemented |
| Controlled benchmark | pending |
| Repeated trials | pending |
| Latency/success analysis | pending |

## Run

Install:

```bash
pip install langchain-ollama langchain-core
```

Make sure Ollama is running and the model is available:

```bash
ollama pull llama3.2:1b
```

Prototype:

```bash
python "reasoning LLM _solve Nqueen problem.py" --n 20 --max-steps 30 --rounds 2
```

Verify a saved trace:

```bash
python scripts/verify_nqueens.py trace.txt
```

## Important limitation

N-Queens is a deliberately simple, verifiable testbed. Success here does not establish general reasoning capability.

The next research question is whether the same inference-time scaling principle transfers to executable coding tasks, where correctness can be checked by running generated programs.
