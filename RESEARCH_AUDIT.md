# Research Audit — Prompt-Time N-Queens Reasoning

## Research question

> Can iterative prompt-time refinement make a small frozen language model behave like a useful search procedure on a verifiable combinatorial problem?

The key variable is **inference-time reasoning budget**, not model weights.

## Original prototype

The original project used `llama3.2:1b`, an n-Queens prompt with a deterministic-looking swap heuristic, and fed the previous response back into a second round.

The README/documented example uses n=20 and reports a final conflict count of 0.

## Important implementation issue

The original function accepted `n` and `max_steps` arguments but hard-coded `n=20` and `max_steps=20` when invoking the prompt.

This branch removes that hard-coding.

## Scientific weaknesses of the original demonstration

1. Only a single problem size was demonstrated.
2. No repeated trials were reported.
3. No baseline one-shot success rate was measured.
4. No fixed inference budget comparison existed.
5. The model's generated conflict counts were not independently verified.
6. The model's claimed greedy swaps were not independently verified.
7. The two-round improvement was shown qualitatively rather than statistically.
8. Temperature/sampling was not controlled.
9. There was no cost/latency measurement.

## Controlled study

Compare inference-time reasoning depth:

- 1 round
- 2 rounds
- 3 rounds
- 5 rounds

Across multiple N-Queens sizes, for example:

- n=8
- n=12
- n=20
- n=30

For each trial independently verify:

- final state length
- row values are a permutation of 0..n-1
- true conflict count
- whether the final state is a valid solution
- number of rounds/model calls
- wall-clock latency

The model must remain frozen.

## Core hypothesis

> Increasing iterative inference-time computation will increase the probability that a small frozen model produces a valid N-Queens solution, at increasing latency cost.

This is falsifiable.

## Baselines

At minimum:

1. one-round generation
2. two-round self-refinement
3. multi-round self-refinement

A stronger later baseline is a non-LLM deterministic local-search solver under a matched compute budget.

## Evidence policy

A generated trace is not evidence of correctness until the final state is independently checked by code.

## Next research question

If iterative self-refinement scales solution probability, can the same test-time-compute principle be transferred from toy combinatorial search to executable coding tasks?
