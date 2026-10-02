import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from prompttime.parser import parse_and_validate,parse_trace,TraceParseError
class ParserTests(unittest.TestCase):
    def test_valid_trace(self):
        text="\n".join(["Initial state for n=4: [1, 3, 0, 2], Conflicts: 0","Final state for n=4: [1, 3, 0, 2], Conflicts: 0"])
        self.assertTrue(parse_and_validate(text,n=4,expected_initial_state=[1,3,0,2],max_steps=20).valid)
    def test_exact_swap_transition(self):
        text="\n".join(["Initial state for n=4: [0, 1, 2, 3], Conflicts: 6","Step 1: State after swap: [1, 0, 2, 3], Conflicts: 2","Final state for n=4: [1, 0, 2, 3], Conflicts: 2"])
        self.assertTrue(parse_and_validate(text,n=4,expected_initial_state=[0,1,2,3],max_steps=20).valid)
    def test_non_swap_is_invalid(self):
        text="\n".join(["Initial state for n=4: [0, 1, 2, 3], Conflicts: 6","Step 1: State after swap: [1, 2, 0, 3], Conflicts: 1","Final state for n=4: [1, 2, 0, 3], Conflicts: 1"])
        result=parse_and_validate(text,n=4,expected_initial_state=[0,1,2,3],max_steps=20)
        self.assertFalse(result.valid); self.assertTrue(any("exactly two" in e for e in result.errors))
    def test_extra_comment_rejected(self):
        with self.assertRaises(TraceParseError):
            parse_trace("Initial state for n=4: [1, 3, 0, 2], Conflicts: 0\nCOMMENT")
if __name__=="__main__": unittest.main()
