from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"src"))
from prompttime.benchmark import load_benchmark,validate_benchmark
from prompttime.config import load_config
from prompttime.model_adapter import OllamaAdapter
from prompttime.prompts import PROMPT_SHA256,PROMPT_VERSION
CONFIG_PATH=ROOT/"configs/experiments/EXP-001.yaml"
BENCHMARK_PATH=ROOT/"benchmarks/manifests/EXP-001-v1.json"
OUTPUT_ROOT=ROOT/"results"/"EXP-001"

def run_preflight(*,check_ollama:bool)->tuple[bool,list[str]]:
    reasons=[]
    if not CONFIG_PATH.exists(): reasons.append(f"experiment config missing: {CONFIG_PATH}")
    if not BENCHMARK_PATH.exists(): reasons.append(f"benchmark manifest missing: {BENCHMARK_PATH}")
    if reasons: return False,reasons
    try: config=load_config(CONFIG_PATH)
    except Exception as exc: return False,[f"invalid experiment config: {type(exc).__name__}: {exc}"]
    benchmark=load_benchmark(BENCHMARK_PATH)
    reasons.extend(validate_benchmark(benchmark,expected_hash=config["benchmark"]["sha256"]))
    if config["benchmark"]["manifest"]!="benchmarks/manifests/EXP-001-v1.json": reasons.append("benchmark manifest path is not frozen")
    if config["prompt"]["version"]!=PROMPT_VERSION: reasons.append("prompt version unresolved")
    if config["prompt"]["sha256"]!=PROMPT_SHA256: reasons.append("prompt hash unresolved")
    OUTPUT_ROOT.mkdir(parents=True,exist_ok=True)
    probe=OUTPUT_ROOT/".write_probe"
    try: probe.write_text("preflight",encoding="utf-8"); probe.unlink()
    except OSError as exc: reasons.append(f"output directory is not writable: {exc}")
    if any(path.name.startswith("latest") for path in OUTPUT_ROOT.glob("*")):
        reasons.append("unsafe fixed/latest output path detected")
    if check_ollama:
        model=config["model"]
        adapter=OllamaAdapter(base_url=model["base_url"],model_id=model["model_id"],
                              temperature=model["temperature"],top_p=model["top_p"],
                              max_output_tokens=model["max_output_tokens"],
                              timeout_seconds=model["timeout_seconds"])
        if not adapter.is_reachable(): reasons.append("Ollama unavailable at configured base URL")
        elif not adapter.model_available(): reasons.append(f"requested Ollama model unavailable: {model['model_id']}")
    return not reasons,reasons

def main()->int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--skip-ollama",action="store_true")
    parser.add_argument("--json",action="store_true")
    args=parser.parse_args()
    ok,reasons=run_preflight(check_ollama=not args.skip_ollama)
    payload={"ready":ok,"reasons":reasons}
    if args.json: print(json.dumps(payload,indent=2))
    elif ok: print("PRE-FLIGHT PASS: real execution gates are satisfied.")
    else:
        print("PRE-FLIGHT FAIL:")
        for reason in reasons: print(f"- {reason}")
    return 0 if ok else 1

if __name__=="__main__": raise SystemExit(main())
