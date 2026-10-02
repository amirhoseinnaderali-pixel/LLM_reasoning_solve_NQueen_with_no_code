from __future__ import annotations
import json
import time
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from .prompts import build_messages

@dataclass(frozen=True)
class ModelResponse:
    content: str
    latency_seconds: float
    input_tokens: int | None
    output_tokens: int | None

class BaseAdapter:
    model_id = "unknown"
    def generate(self, *, n: int, initial_state: list[int], max_steps: int, previous: str, seed: int) -> ModelResponse:
        raise NotImplementedError

class OllamaAdapter(BaseAdapter):
    def __init__(self, *, base_url: str, model_id: str, temperature: float, top_p: float,
                 max_output_tokens: int, timeout_seconds: float):
        self.base_url=base_url.rstrip("/")
        self.model_id=model_id
        self.temperature=temperature
        self.top_p=top_p
        self.max_output_tokens=max_output_tokens
        self.timeout_seconds=timeout_seconds

    def _get(self, path: str) -> dict:
        req=Request(self.base_url+path,method="GET")
        with urlopen(req,timeout=self.timeout_seconds) as response:
            return json.loads(response.read().decode("utf-8"))

    def is_reachable(self) -> bool:
        try:
            self._get("/api/tags")
            return True
        except (OSError,URLError,HTTPError):
            return False

    def model_available(self) -> bool:
        try:
            data=self._get("/api/tags")
        except (OSError,URLError,HTTPError):
            return False
        return self.model_id in {m.get("name") for m in data.get("models",[])}

    def generate(self, *, n: int, initial_state: list[int], max_steps: int, previous: str, seed: int) -> ModelResponse:
        system,user=build_messages(n=n,initial_state=initial_state,max_steps=max_steps,previous=previous)
        payload={
            "model":self.model_id,
            "messages":[{"role":"system","content":system},{"role":"user","content":user}],
            "stream":False,
            "options":{"temperature":self.temperature,"top_p":self.top_p,"seed":seed,"num_predict":self.max_output_tokens},
        }
        req=Request(self.base_url+"/api/chat",data=json.dumps(payload).encode(),
                    headers={"Content-Type":"application/json"},method="POST")
        start=time.perf_counter()
        with urlopen(req,timeout=self.timeout_seconds) as response:
            data=json.loads(response.read().decode("utf-8"))
        latency=time.perf_counter()-start
        content=(data.get("message") or {}).get("content")
        if not isinstance(content,str):
            raise RuntimeError("Ollama response did not contain message.content")
        return ModelResponse(content,latency,data.get("prompt_eval_count"),data.get("eval_count"))

class DeterministicMockAdapter(BaseAdapter):
    model_id="mock/EXP-001"
    def __init__(self):
        self._solution_cache={}
        self._trace_cache={}

    def _solve(self,n:int)->list[int]:
        if n in self._solution_cache:
            return self._solution_cache[n]
        cols=[-1]*n
        rows:set[int]=set(); d1:set[int]=set(); d2:set[int]=set()
        def backtrack(col:int)->bool:
            if col==n: return True
            for row in range(n):
                if row in rows or col-row in d1 or col+row in d2: continue
                cols[col]=row; rows.add(row); d1.add(col-row); d2.add(col+row)
                if backtrack(col+1): return True
                rows.remove(row); d1.remove(col-row); d2.remove(col+row)
            return False
        if not backtrack(0): raise RuntimeError(f"mock solver could not solve n={n}")
        self._solution_cache[n]=list(cols)
        return list(cols)

    @staticmethod
    def _conflicts(state:list[int])->int:
        return sum(
            1 for i in range(len(state)) for j in range(i+1,len(state))
            if state[i]==state[j] or abs(state[i]-state[j])==abs(i-j)
        )

    def _trace(self,n:int,initial:list[int],max_steps:int)->str:
        key=(n,tuple(initial),max_steps)
        if key in self._trace_cache: return self._trace_cache[key]
        target=self._solve(n); state=list(initial)
        lines=[f"Initial state for n={n}: {state}, Conflicts: {self._conflicts(state)}"]
        for i in range(n):
            if state[i]==target[i]: continue
            j=state.index(target[i],i+1)
            state[i],state[j]=state[j],state[i]
            step=len(lines)
            lines.append(f"Step {step}: State after swap: {state}, Conflicts: {self._conflicts(state)}")
            if step>=max_steps: break
        lines.append(f"Final state for n={n}: {state}, Conflicts: {self._conflicts(state)}")
        trace="\n".join(lines); self._trace_cache[key]=trace; return trace

    def generate(self, *, n:int, initial_state:list[int], max_steps:int, previous:str, seed:int)->ModelResponse:
        del previous,seed
        return ModelResponse(self._trace(n,initial_state,max_steps),0.0,None,None)
