from __future__ import annotations
import time
from typing import Any
from .model_adapter import BaseAdapter
from .parser import parse_and_validate
from .verifier import count_conflicts

def run_execution(*, config:dict[str,Any], task:dict[str,Any], seed:int, rounds:int,
                  adapter:BaseAdapter, provenance:dict[str,Any])->dict[str,Any]:
    initial_state=list(task["initial_state"]); n=int(task["n"])
    max_steps=int(config["generation"]["max_trace_steps"])
    round_data=[]; previous=""; total_latency=0.0
    input_sum=output_sum=0; input_ok=output_ok=True; model_calls=0; final_validation=None
    started=time.perf_counter()
    for round_index in range(1,rounds+1):
        try:
            response=adapter.generate(n=n,initial_state=initial_state,max_steps=max_steps,previous=previous,seed=seed)
            model_calls+=1; total_latency+=response.latency_seconds
            if response.input_tokens is None: input_ok=False
            else: input_sum+=int(response.input_tokens)
            if response.output_tokens is None: output_ok=False
            else: output_sum+=int(response.output_tokens)
            validation=parse_and_validate(response.content,n=n,expected_initial_state=initial_state,max_steps=max_steps)
            final_validation=validation
            round_data.append({
                "round":round_index,"raw_output":response.content,
                "parsed":validation.final_state is not None,"trace_valid":validation.valid,
                "conflicts":validation.final_conflicts,"errors":list(validation.errors),
                "latency_seconds":response.latency_seconds,
                "input_tokens":response.input_tokens,"output_tokens":response.output_tokens,
            })
            previous=response.content
        except Exception as exc:
            round_data.append({
                "round":round_index,"raw_output":None,"parsed":False,"trace_valid":False,
                "conflicts":None,"errors":[f"model_error: {type(exc).__name__}: {exc}"],
                "latency_seconds":None,"input_tokens":None,"output_tokens":None,
            })
            break
    elapsed=time.perf_counter()-started
    final_state=final_validation.final_state if final_validation else None
    final_conflicts=final_validation.final_conflicts if final_validation else None
    task_success=bool(final_validation and final_validation.valid and final_conflicts==0)
    if model_calls<rounds: status="model_error"
    elif task_success: status="success"
    elif final_validation and final_validation.valid: status="incorrect"
    else: status="invalid_trace"
    return {
        "experiment_id":config["experiment_id"],"task_id":task["task_id"],"seed":seed,
        "condition":f"R{rounds}","model_id":config["model"]["model_id"],"rounds":rounds,
        "initial_state":initial_state,"initial_conflicts":count_conflicts(initial_state),
        "rounds_data":round_data,"final_state":final_state,"final_conflicts":final_conflicts,
        "task_success":task_success,"model_calls":model_calls,"expected_model_calls":rounds,
        "wall_clock_seconds":elapsed,"input_tokens":input_sum if input_ok else None,
        "output_tokens":output_sum if output_ok else None,
        "total_tokens":input_sum+output_sum if input_ok and output_ok else None,
        "status":status,"evaluated":model_calls==rounds,"provenance":provenance,
        "result_schema_version":1,
    }
