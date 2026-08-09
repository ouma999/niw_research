"""
Reference (oracle) solution for demo_pension_restatement (layered).

This task layers two independent traps:

  Trap 1 (freeze): Section 3 freezes accrual for Group B effective
  September 1 -- eight months into the year. Missing this entirely
  uses the full $360,000 Group B figure unprorated (no_catch_solve).

  Trap 2 (separation): buried in Section 4, independent of the freeze,
  30 of Group B's participants separated from service on March 31 --
  five months before the freeze even took effect. A model that catches
  Trap 1 but not Trap 2 will correctly discount the whole $360,000
  Group B figure to 8/12 and stop there (naive_reflex_solve) -- this
  is the more dangerous failure mode, because the answer already looks
  like it reflects careful reasoning about the freeze.

The correct approach (solve) recognizes Group B is not homogeneous:
the 30 separated participants' $90,000 share stops accruing on March
31 (3/12), while the remaining $270,000 of active Group B participants
are subject to the September 1 freeze (8/12).
"""

GROUP_A_FULL_YEAR = 180_000.0

GROUP_B_TOTAL_FULL_YEAR = 360_000.0
GROUP_B_SEPARATED_FULL_YEAR = 90_000.0
GROUP_B_ACTIVE_FULL_YEAR = GROUP_B_TOTAL_FULL_YEAR - GROUP_B_SEPARATED_FULL_YEAR

MONTHS_ACCRUING_SEPARATED = 3
MONTHS_ACCRUING_ACTIVE_B = 8

INTEREST_COST = 274_000.0
EXPECTED_RETURN = 253_000.0
AMORTIZATION = 52_000.0


def solve():
    group_b_active_prorated = GROUP_B_ACTIVE_FULL_YEAR * (MONTHS_ACCRUING_ACTIVE_B / 12.0)
    group_b_separated_prorated = GROUP_B_SEPARATED_FULL_YEAR * (MONTHS_ACCRUING_SEPARATED / 12.0)
    service_cost = GROUP_A_FULL_YEAR + group_b_active_prorated + group_b_separated_prorated
    return service_cost + INTEREST_COST - EXPECTED_RETURN + AMORTIZATION


def naive_reflex_solve():
    group_b_prorated_uniformly = GROUP_B_TOTAL_FULL_YEAR * (MONTHS_ACCRUING_ACTIVE_B / 12.0)
    service_cost = GROUP_A_FULL_YEAR + group_b_prorated_uniformly
    return service_cost + INTEREST_COST - EXPECTED_RETURN + AMORTIZATION


def no_catch_solve():
    service_cost = GROUP_A_FULL_YEAR + GROUP_B_TOTAL_FULL_YEAR
    return service_cost + INTEREST_COST - EXPECTED_RETURN + AMORTIZATION


def partial_separation_solve():
    """
    Empirically discovered failure tier -- NOT designed into the task.

    Observed in real claude-haiku-4-5-20251001 outputs: 2 of 5 trials
    landed on exactly $523,000 via this route. It was found by reading
    the failing completions, not by anticipating it during task design,
    and it sits between naive_reflex_solve ($493,000) and
    no_catch_solve ($613,000) rather than beyond either.

    The reasoning gets further than naive_reflex_solve does. It
    correctly partitions Group B into the 30 separated participants and
    the 81 continuing ones, and correctly prorates the continuing
    $270,000 to 8/12 for the Section 3 freeze. Its single error is
    taking the separated cohort's *full-year-equivalent* $90,000 at
    face value -- reading that figure as the amount actually accrued
    rather than as the annualized basis to be prorated to 3/12
    ($22,500) for the March 31 separation.

    So it is a failure of Trap 2's arithmetic half only, with Trap 2's
    structural insight intact. That makes it the most interesting tier
    of the three distractors: the partition is right, the freeze is
    right, and the answer is still wrong by $67,500 of service cost.
    """
    group_b_active_prorated = GROUP_B_ACTIVE_FULL_YEAR * (MONTHS_ACCRUING_ACTIVE_B / 12.0)
    group_b_separated_at_face_value = GROUP_B_SEPARATED_FULL_YEAR  # not prorated to 3/12
    service_cost = GROUP_A_FULL_YEAR + group_b_active_prorated + group_b_separated_at_face_value
    return service_cost + INTEREST_COST - EXPECTED_RETURN + AMORTIZATION


if __name__ == "__main__":
    oracle = solve()
    partial = naive_reflex_solve()
    nocatch = no_catch_solve()
    partial_sep = partial_separation_solve()
    print(f"Oracle (both traps caught):         {oracle:,.2f}")
    print(f"Partial (freeze only, subtle):      {partial:,.2f}  gap={abs(oracle - partial) / oracle:.1%}")
    print(f"Partial-sep (separated unprorated): {partial_sep:,.2f}  gap={abs(oracle - partial_sep) / oracle:.1%}  [observed: haiku-4.5]")
    print(f"No-catch (neither trap caught):     {nocatch:,.2f}  gap={abs(oracle - nocatch) / oracle:.1%}")
