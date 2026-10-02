# Current implementation audit

Audit baseline: source commit `8c2d3a7e4f1fc19745db47096639b0730380ad0e`.

## Existing files
- `README.md`
- `reasoning LLM _solve Nqueen problem.py`

No benchmark, verifier, trace parser, experiment config, structured result schema, statistical analysis, test suite or CI existed in the audited HEAD.

## Existing flow
The historical script creates a LangChain Ollama prompt chain and calls `generate_n_queens_trace`. Its `__main__` calls the function exactly twice and feeds the first response into the second call as `previous`.

## Defects
- `generate_n_queens_trace(n, max_steps, previous)` ignored caller values and hard-coded n=20 and max_steps=20.
- `__main__` hard-coded two calls.
- No frozen benchmark.
- No independent verifier or exact pairwise conflict accounting.
- No validation of state transitions or malformed output.
- No multi-seed protocol or provenance.
- No no-overwrite artifact policy.
- No automated paired analysis/plots.
- No CI validation.
- Historical examples were not treated as ground truth by the controlled experiment.

## Preservation
The historical script remains for provenance and now respects its own caller parameters.

## Controlled boundary
Only `src/prompttime/`, `configs/`, `benchmarks/`, `scripts/`, `tests/`, `docs/` and CI constitute the controlled instrument. EXP-001 does not import the historical script.
