import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from prompttime.schemas import validate_result_record
class SchemaTests(unittest.TestCase):
    def test_minimal_valid_shape(self):
        record={"experiment_id":"EXP-001","task_id":"T1","seed":42,"condition":"R1","model_id":"llama3.2:1b",
                "rounds":1,"initial_state":[0,1,2,3],"rounds_data":[],"final_state":[1,3,0,2],"final_conflicts":0,
                "task_success":True,"model_calls":1,"expected_model_calls":1,"wall_clock_seconds":0.1,
                "input_tokens":None,"output_tokens":None,"total_tokens":None,"status":"success","evaluated":True,
                "provenance":{"config_sha256":"x","benchmark_sha256":"y","source_commit":"z","prompt_version":"p","prompt_sha256":"q"}}
        self.assertEqual(validate_result_record(record),[])
if __name__=="__main__": unittest.main()
