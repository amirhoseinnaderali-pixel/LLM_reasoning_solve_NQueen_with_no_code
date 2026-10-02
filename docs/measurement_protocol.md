# Measurement protocol

A state is valid only if length=n, all values are in [0,n-1], it is a permutation, and the exact pairwise conflict count is zero.

For every pair i<j, count one conflict when state[i]==state[j] OR abs(state[i]-state[j])==abs(i-j).

Primary success is final-round task_success.

Trace validity requires the complete final trace to pass parser and independent verifier checks.

Compute accounting records actual model calls and wall-clock time. Input/output/total token fields are populated only from provider counters; otherwise they are null.

Every record includes config hash, benchmark hash, source commit, model identifier, prompt version/hash, seed and task ID.

Every run has a unique run directory created with exist_ok=False.
