import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from prompttime.config import load_config
ROOT=Path(__file__).resolve().parents[1]
class ConfigTests(unittest.TestCase):
    def test_frozen_config(self):
        c=load_config(ROOT/"configs/experiments/EXP-001.yaml")
        self.assertEqual(c["refinement_rounds"],[1,2,4,8]); self.assertEqual(c["seeds"],[42,43,44]); self.assertEqual(c["model"]["model_id"],"llama3.2:1b")
if __name__=="__main__": unittest.main()
