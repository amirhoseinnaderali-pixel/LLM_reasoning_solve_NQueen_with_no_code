# PromptTime-Search: N-Queens Reasoner

This repository contains the historical prompt-time N-Queens prototype and a separate controlled research instrument for EXP-001.

## Historical prototype

The original script is preserved as `reasoning LLM _solve Nqueen problem.py`. It is historical/demo material. Its original examples and prompting behavior are not used by the controlled experiment.

## EXP-001

**Research question:** Does increasing inference-time computation through sequential prompt-time self-refinement improve the probability of producing an objectively correct N-Queens solution while keeping the underlying model and task fixed?

Controlled path:

`task → generation → previous output re-fed → refinement → final candidate → independent verifier`

Conditions: R1, R2, R4 and R8 sequential calls; same frozen task, model, generation settings and seed set.

### Checks

```bash
python -m unittest discover -s tests
python scripts/run_experiment.py --mode validation
python scripts/validate_results.py --input results/validation/<run-id>
python scripts/preflight.py
```

Validation mode uses only a deterministic mock adapter and is not a scientific result.

### Real execution

```bash
python scripts/run_experiment.py --mode smoke
python scripts/run_experiment.py --mode real
```

Real execution requires the exact Ollama model in the frozen configuration and a passing preflight. No early stopping is used.

### Structure

- `src/prompttime/`: controlled implementation
- `configs/experiments/EXP-001.yaml`: frozen configuration
- `benchmarks/manifests/EXP-001-v1.json`: frozen benchmark
- `scripts/`: generation, preflight, execution, validation and analysis
- `tests/`: model-independent tests
- `docs/`: methodology, benchmark, measurement and scientific audit

Runtime artifacts are written under unique run directories; existing runs are never overwritten.
