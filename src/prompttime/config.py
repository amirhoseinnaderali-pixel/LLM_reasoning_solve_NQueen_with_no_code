from __future__ import annotations
import hashlib
import json
from pathlib import Path
from typing import Any
import yaml
from .prompts import PROMPT_SHA256,PROMPT_VERSION

class ConfigError(ValueError): pass

def sha256_file(path:str|Path)->str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def load_config(path:str|Path)->dict[str,Any]:
    data=yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data,dict): raise ConfigError("config must be a mapping")
    required={"experiment_id","status","model","generation","refinement_rounds","seeds","benchmark","prompt"}
    missing=required-set(data)
    if missing: raise ConfigError(f"missing config fields: {sorted(missing)}")
    if data["experiment_id"]!="EXP-001": raise ConfigError("unexpected experiment_id")
    if data["model"]["provider"]!="ollama": raise ConfigError("EXP-001 provider must be ollama")
    if data["model"]["model_id"]!="llama3.2:1b": raise ConfigError("EXP-001 model must remain llama3.2:1b")
    if data["refinement_rounds"]!=[1,2,4,8]: raise ConfigError("refinement_rounds must be [1,2,4,8]")
    if data["seeds"]!=[42,43,44]: raise ConfigError("seeds must be [42,43,44]")
    if data["prompt"]["version"]!=PROMPT_VERSION: raise ConfigError("prompt version mismatch")
    if data["prompt"]["sha256"]!=PROMPT_SHA256: raise ConfigError("prompt hash mismatch")
    if data["benchmark"]["task_count"]!=100: raise ConfigError("benchmark task_count must be 100")
    return data

def canonical_config_sha256(config:dict[str,Any])->str:
    payload=json.dumps(config,sort_keys=True,separators=(",",":"),ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()
