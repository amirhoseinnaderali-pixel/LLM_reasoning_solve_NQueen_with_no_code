from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"src"))
from prompttime.schemas import validate_result_record

def main()->int:
    parser=argparse.ArgumentParser(); parser.add_argument("--input",required=True); args=parser.parse_args()
    root=Path(args.input); meta=root/"run_metadata.json"; records_path=root/"records.jsonl"
    if not meta.exists() or not records_path.exists(): raise SystemExit("expected run_metadata.json and records.jsonl")
    metadata=json.loads(meta.read_text(encoding="utf-8"))
    if metadata.get("status")!="completed": raise SystemExit("run metadata is not marked completed")
    seen=set(); count=0; errors=[]
    for line_number,line in enumerate(records_path.read_text(encoding="utf-8").splitlines(),start=1):
        record=json.loads(line); key=(record["task_id"],int(record["seed"]),record["condition"])
        if key in seen: errors.append(f"duplicate record at line {line_number}: {key}")
        seen.add(key); errors.extend([f"line {line_number}: {e}" for e in validate_result_record(record)]); count+=1
    if metadata.get("record_count") is not None and count!=metadata["record_count"]:
        errors.append(f"record count {count} != metadata {metadata['record_count']}")
    if errors:
        print("RESULT VALIDATION FAIL:"); [print(f"- {e}") for e in errors]; return 1
    print(f"RESULT VALIDATION PASS: {count} records"); return 0
if __name__=="__main__": raise SystemExit(main())
