import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from prompttime.experiment import run_execution
from prompttime.model_adapter import DeterministicMockAdapter
from prompttime.prompts import PROMPT_SHA256,PROMPT_VERSION
CONFIG={"experiment_id":"EXP-001","model":{"model_id":"mock/EXP-001"},"generation":{"max_trace_steps":20}}
class ExperimentTests(unittest.TestCase):
    def test_mock_execution_obeys_round_budget(self):
        task={"task_id":"T1","n":8,"initial_state":[5,3,1,7,6,2,0,4],"seed":42001}
        record=run_execution(config=CONFIG,task=task,seed=42,rounds=4,adapter=DeterministicMockAdapter(),
                             provenance={"config_sha256":"x","benchmark_sha256":"y","source_commit":"z",
                                         "prompt_version":PROMPT_VERSION,"prompt_sha256":PROMPT_SHA256})
        self.assertEqual(record["model_calls"],4); self.assertTrue(record["task_success"]); self.assertEqual(len(record["rounds_data"]),4)
if __name__=="__main__": unittest.main()
