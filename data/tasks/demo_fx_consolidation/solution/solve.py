"""
Reference (oracle) solution for demo_fx_consolidation (v2).

The naive/reflex approach applies the current rate method (the default,
and the method that correctly applies to Subsidiary Norte) uniformly to
Subsidiary Turqueza as well, reporting its translated net income before
remeasurement as the full net income contribution and leaving the
remeasurement loss to sit in OCI. That is the "broken implicit
invariant": the model implicitly assumes translation method is a fixed
property of a subsidiary, when the policy memo explicitly states it
must be reassessed every period against the highly-inflationary
threshold.

The correct approach requires computing Subsidiary Turqueza's trailing
three-year cumulative inflation, confirming it exceeds the ~100%
threshold, and therefore charging the remeasurement loss directly to
net income instead of leaving it in OCI.
"""

INFLATIONARY_THRESHOLD = 1.00  # 100% cumulative over trailing 3 years


def cumulative_three_year_inflation(annual_rates: list[float]) -> float:
    compounded = 1.0
    for rate in annual_rates:
        compounded *= (1.0 + rate)
    return compounded - 1.0


def solve():
    turqueza_inflation_rates = [0.42, 0.35, 0.28]
    cumulative = cumulative_three_year_inflation(turqueza_inflation_rates)
    is_highly_inflationary = cumulative > INFLATIONARY_THRESHOLD

    translated_ni_before_remeasurement = 510_000.0
    remeasurement_loss = 85_000.0

    if is_highly_inflationary:
        # Remeasurement method: the loss hits net income directly.
        return translated_ni_before_remeasurement - remeasurement_loss
    else:
        # Current rate method: the loss (if any) would sit in OCI, not NI.
        return translated_ni_before_remeasurement


def naive_reflex_solve():
    """
    The trap: apply the current rate method to Turqueza the same way
    it correctly applies to Norte, without checking Turqueza's
    trailing three-year cumulative inflation against the threshold.
    The remeasurement loss is left out of net income entirely.
    """
    translated_ni_before_remeasurement = 510_000.0
    return translated_ni_before_remeasurement  # loss ignored, stays in OCI


if __name__ == "__main__":
    cumulative = cumulative_three_year_inflation([0.42, 0.35, 0.28])
    print(f"Turqueza cumulative 3-year inflation: {cumulative:.1%}")

    correct = solve()
    naive = naive_reflex_solve()
    print(f"Oracle (correct) answer:   {correct:,.2f}")
    print(f"Naive/reflex answer:       {naive:,.2f}")
    print(f"Gap:                       {abs(correct - naive):,.2f} "
          f"({abs(correct - naive) / correct:.1%})")
