# Methodology

Round 1 receives the frozen task and fixed instructions.

Round k>1 receives the original task plus the raw output of round k-1 and an explicit instruction to inspect, correct and replace it with a complete trace.

The only state passed between rounds is the original task and previous model output. Evaluator conflict counts, correctness labels, hidden solutions, other-condition results and future-round information are not passed back.

Each round is parsed and independently checked for:
- state length, value domain and permutation property;
- exact recomputed conflicts;
- exact two-position swap transitions;
- exact post-swap state;
- matching reported conflict counts;
- final-state consistency.

The final round is the primary candidate. EXP-001 has no correctness-based early stopping.
