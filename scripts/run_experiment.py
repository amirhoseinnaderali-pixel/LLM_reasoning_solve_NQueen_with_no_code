from __future__ import annotations
import argparse,datetime as dt,json,sys,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"src")); sys.path.insert(0,str(ROOT/"scripts"))
from prompttime.benchmark import load_benchmark,validate_benchmark
from prompttime.config import canonical_config_sha256,load_config,sha256_file
from prompttime.experiment import run_execution
from prompttime.model_adapter import DeterministicMockAdapter,OllamaAdapter
from prompttime.prompts import PROMPT_SHA256,PROMPT_VERSION
from preflight import run_preflight

def new_run_dir(base:Path,prefix:str)->Path:
    run_id=f"{prefix}-{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}"
    path=base/run_id; path.mkdir(parents=True,exist_ok=False); return path

def main()->int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--mode",choices=("validation","smoke","real"),required=True)
    args=parser.parse_args()
    config_path=ROOT/"configs/experiments/EXP-001.yaml"
    benchmark_path=ROOT/"benchmarks/manifests/EXP-001-v1.json"
    config=load_config(config_path); benchmark=load_benchmark(benchmark_path)
    errors=validate_benchmark(benchmark,expected_hash=config["benchmark"]["sha256"])
    if errors: raise SystemExit("benchmark validation failed:\n"+"\n".join(f"- {e}" for e in errors))
    if args.mode=="real":
        ready,reasons=run_preflight(check_ollama=True)
        if not ready: raise SystemExit("real execution blocked by preflight:\n"+"\n".join(f"- {e}" for e in reasons))
        adapter=OllamaAdapter(**{k:config["model"][k] for k in ("base_url","model_id","temperature","top_p","max_output_tokens","timeout_seconds")})
        tasks=list(benchmark.tasks); run_type="real"; prefix="real"; root=ROOT/"results/EXP-001"
    elif args.mode=="smoke":
        ready,reasons=run_preflight(check_ollama=True)
        if not ready: raise SystemExit("smoke execution blocked by runtime gate:\n"+"\n".join(f"- {e}" for e in reasons))
        adapter=OllamaAdapter(**{k:config["model"][k] for k in ("base_url","model_id","temperature","top_p","max_output_tokens","timeout_seconds")})
        tasks=list(benchmark.tasks[:3]); run_type="smoke"; prefix="smoke"; root=ROOT/"results/smoke"
    else:
        adapter=DeterministicMockAdapter(); tasks=list(benchmark.tasks)
        run_type="validation_mock"; prefix="validation"; root=ROOT/"results/validation"
    run_dir=new_run_dir(root,prefix)
    provenance={"config_sha256":sha256_file(config_path),"config_canonical_sha256":canonical_config_sha256(config),
                "benchmark_sha256":benchmark.benchmark_sha256,"source_commit":benchmark.source_commit,
                "prompt_version":PROMPT_VERSION,"prompt_sha256":PROMPT_SHA256,
                "model_id":config["model"]["model_id"] if run_type!="validation_mock" else adapter.model_id}
    metadata={"run_id":run_dir.name,"run_type":run_type,"experiment_id":config["experiment_id"],
              "created_at_utc":dt.datetime.now(dt.timezone.utc).isoformat(),"config":provenance,
              "seed_set":config["seeds"],"refinement_rounds":config["refinement_rounds"],
              "task_count":len(tasks),"status":"running"}
    (run_dir/"run_metadata.json").write_text(json.dumps(metadata,indent=2)+"\n",encoding="utf-8")
    records_path=run_dir/"records.jsonl"
    with records_path.open("w",encoding="utf-8") as records:
        for seed in config["seeds"]:
            for task in tasks:
                for rounds in config["refinement_rounds"]:
                    record=run_execution(config=config,task=task,seed=seed,rounds=rounds,adapter=adapter,provenance=provenance)
                    records.write(json.dumps(record,ensure_ascii=False)+"\n"); records.flush()
    metadata["status"]="completed"; metadata["record_count"]=len(config["seeds"])*len(tasks)*len(config["refinement_rounds"])
    (run_dir/"run_metadata.json").write_text(json.dumps(metadata,indent=2)+"\n",encoding="utf-8")
    print(f"run_id={run_dir.name}"); print(f"artifacts={run_dir}"); print(f"run_type={run_type}")
    return 0
if __name__=="__main__": raise SystemExit(main())
