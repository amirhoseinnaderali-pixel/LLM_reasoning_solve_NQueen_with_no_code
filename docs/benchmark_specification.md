# Benchmark specification

`EXP-001-v1` is a frozen 100-task manifest.

Generation algorithm:
1. task t has seed 42000+t;
2. n is 8, 12, 16 or 20, 25 tasks each;
3. start from range(n);
4. deterministic Fisher-Yates using the 32-bit LCG `state=(1664525*state+1013904223) mod 2^32`;
5. record the resulting permutation and seed.

Materialized benchmark SHA-256:

`4d4bd632d61981e272d813cbf2d9415110ca41149cf24635339e58f2408cd155`

The generator refuses to overwrite an existing manifest.
