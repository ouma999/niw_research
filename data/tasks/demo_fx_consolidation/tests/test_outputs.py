import sys
import os

sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "solution")
)
from solve import solve, naive_reflex_solve, cumulative_three_year_inflation  # noqa: E402

EXPECTED_ANSWER = 425_000.00
TOLERANCE_PCT = 1.0


def within_tolerance(value: float, expected: float, tolerance_pct: float) -> bool:
    return abs(value - expected) / expected <= (tolerance_pct / 100.0)


def test_threshold_crossed():
    cumulative = cumulative_three_year_inflation([0.42, 0.35, 0.28])
    assert cumulative > 1.00, (
        f"Test fixture error: Turqueza's cumulative inflation "
        f"{cumulative:.1%} should exceed the 100% threshold."
    )


def test_oracle_passes():
    result = solve()
    assert within_tolerance(result, EXPECTED_ANSWER, TOLERANCE_PCT), (
        f"Oracle answer {result:,.2f} did not match expected "
        f"{EXPECTED_ANSWER:,.2f} within {TOLERANCE_PCT}%"
    )


def test_naive_reflex_fails():
    result = naive_reflex_solve()
    assert not within_tolerance(result, EXPECTED_ANSWER, TOLERANCE_PCT), (
        f"Naive answer {result:,.2f} incorrectly fell within tolerance "
        f"of {EXPECTED_ANSWER:,.2f} -- task does not discriminate."
    )


if __name__ == "__main__":
    test_threshold_crossed()
    test_oracle_passes()
    test_naive_reflex_fails()
    print("All validation checks passed: threshold crossed, oracle passes, naive reflex fails.")
