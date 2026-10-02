# Scientific audit

## Question alignment
The controlled path isolates sequential prompt-time self-refinement while task and underlying model remain fixed.

## Controls
Model, task, prompt version, temperature, top_p, output cap, seeds and benchmark are frozen.

## Leakage
Only original task, fixed instructions and previous raw output enter later rounds. Verifier feedback, correctness labels, hidden labels and other-condition outcomes are excluded.

## Budget fairness
R1/R2/R4/R8 have fixed call budgets and no early stopping.

## Benchmark integrity
100 committed tasks, fixed distribution and embedded materialized SHA-256.

## Verifier independence
Pure Python pairwise verifier; no LLM or evaluator feedback dependency.

## Reproducibility
Config, benchmark, source commit, prompt hash, model ID, seed and task ID are stored in provenance.

## Known limitations
Ollama/runtime behavior and wall-clock timing are environment dependent; provider token counts may be unavailable; the benchmark covers four N values; empirical claims require an actual real run.
