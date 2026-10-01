# Results

No new controlled benchmark has been executed in this branch.

## Historical evidence

The original README contains a qualitative n=20 example ending at a reported conflict count of 0.

That is preserved as historical evidence only.

## Required controlled metrics

| Metric | Definition |
|---|---|
| Success rate | fraction of trials whose final state is independently conflict-free |
| True final conflicts | independently computed conflict count |
| Rounds | number of model calls |
| Latency | wall-clock inference time |
| Valid-state rate | fraction of outputs with a valid permutation |
| Budget | rounds × configured max steps |

The primary analysis should plot success rate against inference budget.
