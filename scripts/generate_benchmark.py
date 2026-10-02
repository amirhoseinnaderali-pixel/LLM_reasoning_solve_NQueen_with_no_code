from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
EXPECTED_SHA256="4d4bd632d61981e272d813cbf2d9415110ca41149cf24635339e58f2408cd155"

def lcg_shuffle(n:int,seed:int)->list[int]:
    state=seed & 0xFFFFFFFF; values=list(range(n))
    for i in range(n-1,0,-1):
        state=(1664525*state+1013904223)&0xFFFFFFFF
        j=state%(i+1); values[i],values[j]=values[j],values[i]
    return values

def canonical_tasks(tasks:list[dict])->bytes:
    return json.dumps(tasks,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()

def main()->int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",required=True)
    parser.add_argument("--source-commit",required=True)
    args=parser.parse_args()
    output=Path(args.output)
    if output.exists(): raise SystemExit(f"refusing to overwrite existing benchmark: {output}")
    tasks=[]; index=1
    for n in (8,12,16,20):
        for _ in range(25):
            seed=42000+index
            tasks.append({"task_id":f"EXP-001-T{index:03d}","n":n,"initial_state":lcg_shuffle(n,seed),"seed":seed})
            index+=1
    digest=hashlib.sha256(canonical_tasks(tasks)).hexdigest()
    if digest!=EXPECTED_SHA256: raise SystemExit(f"generator integrity failure: {digest} != {EXPECTED_SHA256}")
    manifest={"benchmark_id":"EXP-001-v1","experiment_id":"EXP-001","format_version":1,
              "generation_algorithm":"32-bit LCG Fisher-Yates shuffle: state=(1664525*state+1013904223) mod 2^32",
              "generation_algorithm_version":"1","task_count":100,"tasks":tasks,
              "source_commit":args.source_commit,"benchmark_sha256":digest}
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
    return 0

if __name__=="__main__": raise SystemExit(main())
