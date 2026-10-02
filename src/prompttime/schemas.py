from typing import Any

REQUIRED_RESULT_FIELDS = {
    "experiment_id","task_id","seed","condition","model_id","rounds",
    "initial_state","rounds_data","final_state","final_conflicts","task_success",
    "model_calls","expected_model_calls","wall_clock_seconds","input_tokens",
    "output_tokens","total_tokens","status","evaluated","provenance",
}

def validate_result_record(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    missing = sorted(REQUIRED_RESULT_FIELDS - set(record))
    if missing:
        errors.append(f"missing fields: {missing}")
    if not isinstance(record.get("rounds_data"), list):
        errors.append("rounds_data must be a list")
    if not isinstance(record.get("task_success"), bool):
        errors.append("task_success must be boolean")
    if not isinstance(record.get("evaluated"), bool):
        errors.append("evaluated must be boolean")
    if record.get("model_calls", 0) > record.get("expected_model_calls", 0):
        errors.append("model_calls cannot exceed expected_model_calls")
    provenance = record.get("provenance")
    if not isinstance(provenance, dict):
        errors.append("provenance must be an object")
    else:
        for field in ("config_sha256","benchmark_sha256","source_commit","prompt_version","prompt_sha256"):
            if field not in provenance:
                errors.append(f"provenance missing {field}")
    if record.get("task_success") and record.get("final_conflicts") != 0:
        errors.append("successful record must have final_conflicts == 0")
    return errors
