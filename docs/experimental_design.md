# Experimental design

- 100 frozen tasks
- 3 seeds: 42, 43, 44
- 4 refinement budgets: R1, R2, R4, R8
- 1 model: `llama3.2:1b`

Nominal task-condition-seed executions: 100 × 3 × 4 = 1200.

Nominal model calls across a complete run: 100 × 3 × (1+2+4+8) = 4500.

Task distribution: 25 each of n=8,12,16,20.

Initial permutations are deterministic and committed. Generation settings are temperature=0.2, top_p=0.9, max output tokens=2048, fixed seed per condition and round.

Provider token counts are recorded only when exposed by the provider; otherwise they remain null.

Claims must be limited to what the realized paired measurements support.
