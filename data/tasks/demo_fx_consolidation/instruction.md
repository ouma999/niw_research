# Subsidiary Net Income Contribution -- Consolidated Reporting Group

You are the technical accounting lead determining how much of
Subsidiary Turqueza's current-year results should flow into
consolidated net income (as opposed to other comprehensive income)
under ASC 830.

Two source materials are provided below. Use only the information in
these two sources.

## Source 1: Foreign Currency Translation Policy Memo (policy_memo.pdf)

> **Section 2. Highly Inflationary Economies**
>
> If a subsidiary's cumulative inflation over the three years
> preceding the current reporting date exceeds approximately 100%, the
> subsidiary's economy is deemed highly inflationary and its
> functional currency is deemed to be the US dollar (the reporting
> currency) instead of its local currency. For any subsidiary meeting
> this condition in the current fiscal year, the remeasurement method
> applies for that year instead of the current rate method: monetary
> items are remeasured at the current rate, nonmonetary items are
> remeasured at historical rates, and any resulting remeasurement gain
> or loss is recognized directly in net income for the period, not in
> OCI.
>
> This determination is made independently for each subsidiary, every
> period, based on that subsidiary's own trailing three-year
> cumulative inflation. A subsidiary's translation method is not a
> fixed, one-time election; it must be reassessed each period against
> the threshold in this section.

(Section 1 states the default current rate method used for all
subsidiaries that do not meet the Section 2 threshold: translated net
income flows to consolidated net income as computed, with any
translation adjustment recorded in OCI rather than net income.)

## Source 2: Subsidiary Financial Data Extract (subsidiary_data.db)

**Table: subsidiary_inflation**

| Subsidiary            | Year        | Annual Inflation Rate |
|------------------------|-------------|------------------------:|
| Subsidiary Norte        | 2 years ago  | 3.0%                    |
| Subsidiary Norte        | 1 year ago   | 4.0%                    |
| Subsidiary Norte        | Current year | 3.5%                    |
| Subsidiary Turqueza      | 2 years ago  | 42.0%                   |
| Subsidiary Turqueza      | 1 year ago   | 35.0%                   |
| Subsidiary Turqueza      | Current year | 28.0%                   |

**Table: subsidiary_financials**

| Subsidiary            | Translated Net Income Before Remeasurement (USD) | Remeasurement Loss on Net Monetary Position (USD) |
|------------------------|---------------------------------------------------:|------------------------------------------------------:|
| Subsidiary Norte        | $240,000                                             | $0                                                       |
| Subsidiary Turqueza      | $510,000                                             | $85,000                                                  |

## What to compute

Determine Subsidiary Turqueza's contribution to consolidated net
income (USD) for the current fiscal year, applying the correct
translation method under the policy memo.

## Output format

State your final answer as a single dollar amount, no commas or
currency symbols, on its own line in the exact form:

FINAL ANSWER: <number>
