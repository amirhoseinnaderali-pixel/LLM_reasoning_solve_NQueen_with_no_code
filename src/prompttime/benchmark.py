from __future__ import annotations
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

EXPECTED_COUNTS = {8:25,12:25,16:25,20:25}

@dataclass(frozen=True)
class Benchmark:
    benchmark_id: str
    experiment_id: str
    task_count: int
    tasks: tuple[dict[str, Any], ...]
    source_commit: str
    benchmark_sha256: str

def compute_benchmark_sha256(tasks: list[dict[str, Any]]) -> str:
    payload = json.dumps(tasks, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()

def load_benchmark(path: str | Path) -> Benchmark:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return Benchmark(data["benchmark_id"],data["experiment_id"],int(data["task_count"]),
                     tuple(data["tasks"]),data["source_commit"],data["benchmark_sha256"])

def validate_benchmark(benchmark: Benchmark, *, expected_hash: str | None = None) -> list[str]:
    errors: list[str] = []
    tasks = list(benchmark.tasks)
    if benchmark.task_count != 100 or len(tasks) != 100:
        errors.append("benchmark must contain exactly 100 tasks")
    ids = [task.get("task_id") for task in tasks]
    if len(set(ids)) != len(ids):
        errors.append("task IDs are not unique")
    by_n: dict[int,int] = {}
    for task in tasks:
        n = int(task.get("n",-1))
        state = task.get("initial_state")
        by_n[n] = by_n.get(n,0)+1
        if not isinstance(state,list) or sorted(state) != list(range(n)):
            errors.append(f"invalid initial permutation for {task.get('task_id')}")
        if task.get("seed") is None:
            errors.append(f"missing seed for {task.get('task_id')}")
    if by_n != EXPECTED_COUNTS:
        errors.append(f"task distribution {by_n} != {EXPECTED_COUNTS}")
    calculated = compute_benchmark_sha256(tasks)
    if calculated != benchmark.benchmark_sha256:
        errors.append("materialized benchmark SHA-256 does not match embedded benchmark_sha256")
    if expected_hash is not None and calculated != expected_hash:
        errors.append("benchmark SHA-256 does not match experiment configuration")
    return errors
