from scripts.verify_nqueens import count_conflicts, verify


def test_known_solution():
    assert count_conflicts([1, 3, 0, 2]) == 0


def test_invalid_solution():
    result = verify("Final state for n=4: [0, 1, 2, 3], Conflicts: 6")
    assert result["success"] is False
