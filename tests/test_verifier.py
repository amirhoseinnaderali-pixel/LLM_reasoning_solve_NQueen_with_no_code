import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from prompttime.verifier import count_conflicts,verify_state
class VerifierTests(unittest.TestCase):
    def test_known_solution(self):
        self.assertEqual(count_conflicts([1,3,0,2]),0); self.assertTrue(verify_state([1,3,0,2],4).valid)
    def test_invalid_row_conflict(self):
        result=verify_state([0,0,1,2],4); self.assertFalse(result.valid); self.assertGreater(result.conflicts,0)
    def test_invalid_domain_and_permutation(self):
        result=verify_state([0,1,2,4],4); self.assertFalse(result.valid); self.assertTrue(any("outside" in e for e in result.errors))
    def test_pair_counting_unique(self): self.assertEqual(count_conflicts([0,1,2,3]),6)
if __name__=="__main__": unittest.main()
