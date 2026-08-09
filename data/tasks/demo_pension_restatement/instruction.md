# Net Periodic Pension Cost -- Meridian Industrial Corp.

You are the technical accounting lead recomputing net periodic pension
cost for Meridian Industrial Corp.'s defined benefit plan for the
current fiscal year (January 1 to December 31) under ASC 715.

Four source materials are provided below, extracted from the plan's
underlying records. Use only the information in these four sources.

## Source 1: Census Summary (from plan_data.db, table census_summary)

| Group   | Hire Date Cutoff              | Participants | Full-Year Service Cost |
|---------|--------------------------------|-------------:|------------------------:|
| Group A | hired before 2010-01-01        | 64            | $180,000                |
| Group B | hired on or after 2010-01-01   | 111           | $360,000                |

Note: prior_period_ledger figures also exist in this database but
reflect prior-period assumptions and prior-period plan terms. They are
provided for reference only and should not be used as the current
period's answer.

## Source 2: Separations Log (from plan_data.db, table separations_log)

| Group   | Separation Reason  | Participants | Separation Effective Date | Full-Year-Equivalent Service Cost |
|---------|---------------------|-------------:|-----------------------------|-------------------------------------:|
| Group B | Vested termination   | 30            | 2024-03-31                    | $90,000                               |

The full-year-equivalent service cost shown here is the portion of
Group B's $360,000 full-year service cost attributable to these 30
separated participants (their average tenure and pay band differ from
the rest of Group B, so this is not a simple headcount-proportional
share).

## Source 3: Actuarial Assumptions Workbook (assumptions.xlsx)

**Tab: Discount_Rate**
| Period          | Discount Rate |
|-----------------|--------------:|
| Prior period     | 5.25%          |
| Current period   | 4.60%          |

**Tab: Mortality_Table**
| Period          | Table Version Code                |
|-----------------|------------------------------------|
| Prior period     | RP-2014-TotalDataset-MP2019        |
| Current period   | RP-2014-TotalDataset-MP2021        |

**Tab: Expected_Return**
| Period          | Expected Long-Term Return on Plan Assets |
|-----------------|------------------------------------------:|
| Prior period     | 5.50%                                      |
| Current period   | 5.50%                                      |

**Tab: Amortization_Schedule**
| Component                              | Current Period Amount |
|-----------------------------------------|------------------------:|
| Amortization of net actuarial loss      | $52,000                 |

The current-period interest cost, already computed by the plan's
actuary reflecting the current-period discount rate and the updated
mortality table above, is **$274,000**. The current-period expected
return on plan assets, already computed reflecting the current-period
assumptions above, is **$253,000**. Neither of these two figures
requires further adjustment by you.

## Source 4: Plan Document and Actuarial Notes (plan_document.pdf)

> **Section 3. Plan Amendment -- Accrual Freeze**
>
> Effective September 1 of the current fiscal year, the Plan was
> amended to freeze future benefit accruals for all participants hired
> on or after January 1, 2010. Participants hired before January 1,
> 2010 ("Grandfathered Participants") continue to accrue benefits
> under the existing formula without change, through the remainder of
> the current fiscal year and thereafter until a further amendment is
> adopted.
>
> No other terms of the Plan were changed by this amendment.
>
> **Section 4. Separation from Service**
>
> Independent of the amendment described in Section 3, credited
> service accrual for any participant ceases as of that participant's
> individual date of separation from service, regardless of the
> participant's group under Section 3. A participant who separates
> from service prior to September 1 of the current fiscal year accrues
> service cost only through that participant's own separation date,
> not through September 1. This rule applies without exception and is
> unaffected by, and independent of, the Section 3 amendment.
>
> Separation data for the current fiscal year is provided in the
> plan's separations log. This amendment does not affect
> vested-terminated or retired participants' previously accrued
> (frozen) benefit obligations, which are unaffected by either the
> freeze or ongoing separations.
>
> **Section 5. Amortization of Net Actuarial Loss**
>
> ...amortized on a straight-line basis... The current-period
> amortization amount is disclosed in the amortization schedule
> workbook and is unaffected by Sections 3 or 4 above.

## What to compute

Determine the net periodic pension cost recognized for the full
current fiscal year, combining:

1. Service cost (accounting correctly for the effect of both the
   Section 3 plan amendment and Section 4 separations on each
   participant group's accrual for the year)
2. Interest cost
3. Expected return on plan assets
4. Amortization of net actuarial loss

## Output format

Prorate any partial-year accrual on a whole-month basis, not on actual
day counts (January through August = 8/12; January through March =
3/12).

State your final answer as a single dollar amount, no commas or
currency symbols, on its own line in the exact form:

FINAL ANSWER: <number>
