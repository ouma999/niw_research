import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "solution"))
from solve import solve, naive_reflex_solve, no_catch_solve  # noqa: E402

EXPECTED_ANSWER = 455_500.00
TOLERANCE_PCT = 1.0


def within_tolerance(value, expected, tolerance_pct):
    return abs(value - expected) / expected <= (tolerance_pct / 100.0)


def test_oracle_passes():
    result = solve()
    assert within_tolerance(result, EXPECTED_ANSWER, TOLERANCE_PCT)


def test_partial_catch_naive_fails():
    result = naive_reflex_solve()
    assert not within_tolerance(result, EXPECTED_ANSWER, TOLERANCE_PCT)


def test_no_catch_naive_fails():
    result = no_catch_solve()
    assert not within_tolerance(result, EXPECTED_ANSWER, TOLERANCE_PCT)


def test_partial_catch_closer_than_no_catch():
    oracle = solve()
    partial_gap = abs(naive_reflex_solve() - oracle)
    nocatch_gap = abs(no_catch_solve() - oracle)
    assert partial_gap < nocatch_gap


if __name__ == "__main__":
    test_oracle_passes()
    test_partial_catch_naive_fails()
    test_no_catch_naive_fails()
    test_partial_catch_closer_than_no_catch()
    print("All validation checks passed.")
