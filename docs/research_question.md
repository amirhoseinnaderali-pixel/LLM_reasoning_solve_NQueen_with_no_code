# Research question

Does increasing inference-time computation through sequential prompt-time self-refinement improve the probability of producing an objectively correct N-Queens solution while keeping the underlying model and task fixed?

## Hypothesis
Increasing sequential prompt-time self-refinement may change final solution success probability. The experiment does not assume a direction or magnitude.

## Independent variable
R1=1 call, R2=2 calls, R4=4 calls, R8=8 calls.

## Primary dependent variable
`task_success=1` iff the final candidate passes the independent verifier.

## Secondary outcomes
Mean/median final conflicts, initial conflicts, conflict reduction, trace validity, malformed/invalid rate, model calls, wall-clock latency and provider-reported tokens when available.

## Controls
Model, task, prompt version, generation limits, temperature, top_p, seeds, benchmark and evaluator are fixed. Verifier feedback and hidden correctness signals are never returned to the model.
