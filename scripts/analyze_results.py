from __future__ import annotations
import argparse,json,statistics
from collections import defaultdict
from pathlib import Path

def find_real_run(input_path:Path)->Path:
    if (input_path/"run_metadata.json").exists(): return input_path
    candidates=[]
    for p in input_path.glob("*/run_metadata.json"):
        meta=json.loads(p.read_text(encoding="utf-8"))
        if meta.get("run_type")=="real" and meta.get("status")=="completed":
            candidates.append((meta.get("created_at_utc",""),p.parent))
    if not candidates:
        raise SystemExit("no completed real EXP-001 run found; mock/smoke artifacts are not scientific results")
    return sorted(candidates,reverse=True)[0][1]

def summarize(rows):
    groups=defaultdict(list)
    for r in rows: groups[r["condition"]].append(r)
    out={}
    for condition in ("R1","R2","R4","R8"):
        data=groups.get(condition,[])
        evaluated=[r for r in data if r["evaluated"]]
        if len(evaluated) != 300:
            raise SystemExit(f"{condition} is incomplete: expected 300 evaluated task-seed units, found {len(evaluated)}")
        successes=[r for r in evaluated if r["task_success"]]
        conflicts=[r["final_conflicts"] for r in evaluated if r["final_conflicts"] is not None]
        latencies=[r["wall_clock_seconds"] for r in evaluated]
        valid=[r for r in evaluated if r["rounds_data"] and r["rounds_data"][-1]["trace_valid"]]
        calls=[r["model_calls"] for r in data]
        out[condition]={
            "evaluated":len(evaluated),"successful":len(successes),
            "success_rate":len(successes)/len(evaluated),
            "mean_final_conflicts":statistics.mean(conflicts) if conflicts else None,
            "median_final_conflicts":statistics.median(conflicts) if conflicts else None,
            "trace_validity_rate":len(valid)/len(evaluated),
            "malformed_or_invalid_rate":1-len(valid)/len(evaluated),
            "mean_model_calls":statistics.mean(calls),
            "mean_wall_clock_seconds":statistics.mean(latencies),
            "median_wall_clock_seconds":statistics.median(latencies),
        }
    return out

def paired(rows,baseline,candidate):
    idx={(r["task_id"],int(r["seed"]),r["condition"]):r for r in rows}
    diffs=[]
    for r in rows:
        if r["condition"]!=baseline: continue
        key=(r["task_id"],int(r["seed"]))
        a=idx.get((*key,baseline)); b=idx.get((*key,candidate))
        if a and b and a["evaluated"] and b["evaluated"]:
            diffs.append(int(bool(b["task_success"]))-int(bool(a["task_success"])))
    return {"comparison":f"{baseline}_vs_{candidate}","paired_units":len(diffs),
            "success_difference_mean":statistics.mean(diffs) if diffs else None,
            "candidate_wins":sum(d>0 for d in diffs),"baseline_wins":sum(d<0 for d in diffs),"ties":sum(d==0 for d in diffs)}

def make_plots(summary,output):
    import matplotlib.pyplot as plt
    x=[1,2,4,8]; labels=["R1","R2","R4","R8"]
    plots=[
        ("success_rate_vs_refinement.png",[summary[c]["success_rate"] for c in labels],"Success rate"),
        ("final_conflicts_vs_refinement.png",[summary[c]["mean_final_conflicts"] for c in labels],"Mean final conflict count"),
        ("invalid_trace_rate_vs_refinement.png",[summary[c]["malformed_or_invalid_rate"] for c in labels],"Invalid-trace rate"),
        ("latency_vs_refinement.png",[summary[c]["mean_wall_clock_seconds"] for c in labels],"Mean wall-clock seconds"),
    ]
    for filename,values,ylabel in plots:
        fig=plt.figure(); ax=fig.gca(); ax.plot(x,values,marker="o")
        ax.set_xlabel("Sequential refinement rounds"); ax.set_ylabel(ylabel)
        fig.savefig(output/filename,dpi=150,bbox_inches="tight"); plt.close(fig)

def main()->int:
    parser=argparse.ArgumentParser(); parser.add_argument("--input",required=True); args=parser.parse_args()
    run=find_real_run(Path(args.input))
    rows=[json.loads(x) for x in (run/"records.jsonl").read_text().splitlines() if x.strip()]
    if len(rows)!=1200:
        raise SystemExit(f"incomplete real run: expected 1200 records, found {len(rows)}")
    summary=summarize(rows)
    paired_out={c:paired(rows,"R1",c) for c in ("R2","R4","R8")}
    output=run/"analysis"; output.mkdir(exist_ok=False)
    (output/"summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    (output/"paired_comparisons.json").write_text(json.dumps(paired_out,indent=2)+"\n")
    make_plots(summary,output)
    print(f"analysis={output}")
    return 0

if __name__=="__main__": raise SystemExit(main())
