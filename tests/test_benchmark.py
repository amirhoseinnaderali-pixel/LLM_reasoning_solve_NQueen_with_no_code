import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from prompttime.benchmark import compute_benchmark_sha256,load_benchmark,validate_benchmark
ROOT=Path(__file__).resolve().parents[1]
SHA="4d4bd632d61981e272d813cbf2d9415110ca41149cf24635339e58f2408cd155"
class BenchmarkTests(unittest.TestCase):
    def test_frozen_manifest_integrity(self):
        b=load_benchmark(ROOT/"benchmarks/manifests/EXP-001-v1.json"); self.assertEqual(validate_benchmark(b,expected_hash=SHA),[])
    def test_hash_stable(self):
        b=load_benchmark(ROOT/"benchmarks/manifests/EXP-001-v1.json"); self.assertEqual(compute_benchmark_sha256(list(b.tasks)),SHA)
if __name__=="__main__": unittest.main()
