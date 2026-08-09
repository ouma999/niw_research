# Evaluation Summary — Measurement Pass

Three evaluation passes run against the Anthropic API.

Passes 1 and 2 below were pure measurement: no task files were modified
while they ran. In a later step, `demo_pension_restatement/solution/solve.py`
gained a fourth reference tier (`partial_separation_solve`) documenting a
failure mode discovered *from* these results — see "Failure modes are
qualitatively distinct" below. No oracle answer, instruction, or pass/fail
logic was changed, so the numbers reported here remain valid as recorded.

Confidence intervals are as reported by `stats_report.py` (95%, binomial).

## Pass 1 — claude-sonnet-4-6, 15 trials/task (30 calls)

| Task | Failure family | Pass rate | 95% CI |
|------|----------------|----------:|--------|
| demo_fx_consolidation | assumption_violation | 15/15 (100%) | [80%, 100%] |
| demo_pension_restatement | temporal_coupling | 15/15 (100%) | [80%, 100%] |
| **Model overall** | — | **30/30 (100%)** | **[89%, 100%]** |

Answer distribution was fully degenerate: all 15 pension responses parsed
to exactly `455500` and all 15 FX responses to exactly `425000`. No
distractor tier was hit even once.

## Pass 2 — claude-haiku-4-5-20251001, 5 trials/task (10 calls)

| Task | Failure family | Pass rate | 95% CI |
|------|----------------|----------:|--------|
| demo_fx_consolidation | assumption_violation | 3/5 (60%) | [23%, 88%] |
| demo_pension_restatement | temporal_coupling | 3/5 (60%) | [23%, 88%] |
| **Model overall** | — | **6/10 (60%)** | **[31%, 83%]** |

## Does the Sonnet CI still overlap 100%?

Yes — it necessarily does. With zero observed failures the point estimate
is pinned at 100% and the interval is one-sided; what moves with sample
size is only the *lower* bound. Going 5 → 15 trials tightened that bound
from 57% to 80%.

So the interval is **not** yet tight enough to say the task fails to
discriminate "at any reasonable confidence level." What the data licenses
is the weaker claim: Sonnet's true pass rate is ≥80% (95% confidence) on
each task individually, and ≥89% pooled. A true rate of 80–85% would still
produce occasional failures that 15 trials could plausibly miss.

By the rule of three (0 failures in *n* trials ⇒ 95% upper bound on the
failure rate ≈ 3/*n*), reaching stronger claims requires:

| Trials, 0 failures | 95% lower bound on pass rate |
|-------------------:|------------------------------|
| 15 (current) | 80% |
| 30 | 90% |
| 60 | 95% |
| 100 | 97% |

A defensible "this task does not discriminate against Sonnet" claim needs
roughly **n ≥ 60 per task**. That is a cheap run and is the recommended
next measurement step.

> **Superseded by Pass 3.** That n = 60 run has since been executed; see
> below. The rule-of-three table above applies only to the zero-failure
> case, and the pension task did produce failures at n = 60, so its
> interval is now two-sided rather than pinned at 100%.

## Pass 3 — claude-sonnet-4-6, 60 trials/task (120 calls)

| Task | Failure family | Pass rate | 95% CI |
|------|----------------|----------:|--------|
| demo_fx_consolidation | assumption_violation | 60/60 (100%) | [94%, 100%] |
| demo_pension_restatement | temporal_coupling | 58/60 (97%) | [89%, 99%] |
| **Model overall** | — | **118/120 (98%)** | **[94%, 100%]** |

This is the definitive Sonnet measurement and it resolves the question the
earlier passes could not.

**FX reaches the target cleanly.** 60/60 with a 94% lower bound. The
non-discrimination claim is now defensible for this task: Sonnet's true
pass rate is ≥94% at 95% confidence.

**Pension breaks 100% — but not on mechanism.** 58/60 gives [89%, 99%], an
interval that excludes 100% at the upper end. Taken at face value this
looks like the first evidence of the task biting. It is not. Reading both
failing completions shows neither is a conceptual miss, and the
distinction matters more than the point estimate.

### Failure autopsy: trial36 — arithmetic slip, both traps caught

Landed on **$435,500** (oracle $455,500; a $20,000 gap). The reasoning is
correct in full. It partitioned Group B, prorated the separated cohort to
3/12 = $22,500, prorated the active cohort to 8/12 = $180,000, and
summed Group B to $202,500 — every step of both traps handled.

It then wrote:

> Service cost = Group A + Group B = $180,000 + $202,500 = **$362,500**

That sum is $382,500. A single addition error on the final aggregation
line, downstream of all the reasoning the task is designed to probe. Both
traps were caught; the arithmetic failed afterward.

### Failure autopsy: trial57 — harness truncation, not a model failure

Scored as a failure because no `FINAL ANSWER:` line could be parsed. The
response ends mid-word:

> Rounding to nearest dollar: **$455

It had already computed $455,295.08 — within 1% of the oracle, and a
**passing** answer — using day-count proration (91/366 and 244/366,
correctly noting 2024 is a leap year). The completion was cut off before
it could print the answer line.

Root cause: `model_runner.py` set `max_tokens = 1024`. The response hit
the ceiling. This is a measurement-validity defect in the harness, not a
property of the model: the trial was lost to a buffer size, and any
longer-reasoning model or richer task would lose more.

### Corrected reading

Scored on mechanism rather than on the final number, Sonnet is **60/60 on
the pension task**. The 58/60 figure is one arithmetic slip plus one
harness artifact. The benchmark's binary verifier cannot separate these
from conceptual failures — the same limitation documented for FX sign
errors below, now confirmed to affect the pension task too, and now with
a second cause (truncation) that is purely infrastructural.

### Follow-up actions taken

1. **`max_tokens` raised 1024 → 4096** for `AnthropicClient`,
   `OpenAIClient`, and `GeminiClient` in `src/model_runner.py`. Removes
   the truncation failure mode that cost trial57.
2. **Whole-month proration clarified** in the pension task's
   `instruction.md` "Output format" section (January–August = 8/12,
   January–March = 3/12). Three of 60 responses prorated on actual days,
   landing at $455,295–$455,377. All passed, but only because the 1%
   tolerance is wide enough to absorb them — a narrower tolerance would
   have failed correct reasoning. The oracle answer and the
   `FINAL ANSWER:` format were left unchanged.

Both changes postdate Pass 3, so its numbers reflect the *old*
`max_tokens` and the *un*clarified instruction. Pass 3 is therefore not
directly comparable to any future run; a re-run under the fixed harness
is needed before the two are pooled.

## Does Haiku differ meaningfully? (capability gradient)

Yes, and this is the more useful finding. The 100% → 60% separation is
statistically supported when the tasks are pooled:

- Pension alone (15/15 vs 3/5): Fisher exact **p = 0.053**
- FX alone (15/15 vs 3/5): Fisher exact **p = 0.053**
- Pooled (30/30 vs 6/10): Fisher exact **p = 0.0023**

Per-task the comparison sits just at the edge of conventional significance
— an artifact of Haiku's small n = 5, not of a weak effect. Pooled, the
gradient is solid. Raising Haiku to 15 trials would settle each task
individually.

### Failure modes are qualitatively distinct — and neither matches the modeled distractors

This is the part most relevant to the paper. Haiku's failures did **not**
land on either tier encoded in `solve.py`.

**Pension (2/5 failures, both `523000`).** Haiku's reasoning was largely
correct: it partitioned Group B into 30 separated + 81 continuing, and
correctly prorated the continuing $270,000 to 8/12 = $180,000 for the
Section 3 freeze. Its single error was taking the separated cohort's
*full-year-equivalent* $90,000 at face value instead of prorating it to
3/12 = $22,500. Service cost $450,000 vs. oracle $382,500.

This is a **third failure tier** not represented in `solve.py`, which
models only `naive_reflex_solve` (493,000 — uniform 8/12, no partition)
and `no_catch_solve` (613,000 — no proration at all). The observed mode
sits *between* them: the structural insight lands, the proration
arithmetic on the separated cohort does not. Notably, it is a failure of
the trap's second half only — evidence the layered design does separate
partial understanding from full understanding, just along a different
seam than anticipated.

**FX (2/5 failures, both `595000`).** Haiku correctly identified the
highly inflationary economy and correctly concluded that remeasurement
gains/losses flow through net income rather than OCI — i.e. it did *not*
fall for the targeted `assumption_violation` trap. It then **added** the
$85,000 remeasurement loss instead of subtracting it ($510,000 + $85,000
rather than $510,000 − $85,000). This is a sign error, not the failure
family the task is designed to probe.

### Implication

Aggregate pass rate conflates two very different things here. Haiku's FX
failures are arithmetic noise and arguably should not count as
`assumption_violation` evidence at all; its pension failures *are*
on-mechanism but occupy an unmodeled tier. Scoring on the final number
alone cannot tell these apart. Tagging responses by which distractor tier
they land on — and adding the observed 523,000 tier to `solve.py` — would
make the benchmark measure what it claims to measure.

Recommended next steps (all measurement/design, none applied here):

1. ~~Sonnet at n = 60/task to firm up the non-discrimination claim.~~
   **Done — see Pass 3.**
2. Haiku at n = 15/task for per-task significance. *(still open)*
3. ~~Add a `separated_cohort_unprorated` tier (523,000) to the pension
   `solve.py` distractor set.~~ **Done — added as
   `partial_separation_solve()`.**
4. Consider whether FX sign errors should be tagged separately from
   assumption violations in `failure_tagger.py`. *(still open — Pass 3
   adds two more non-conceptual categories to the case for this:
   arithmetic slips and truncated completions.)*

## Known scoring limitation

The FX task's binary pass/fail verifier cannot distinguish an arithmetic
sign error from a conceptual failure, and in the Haiku run it scored the
former as the latter.

Both of Haiku's `demo_fx_consolidation` failures (2/5 trials) landed on
exactly **$595,000**. Reading the completions shows the conceptual
reasoning was entirely correct:

1. It computed cumulative three-year inflation as
   (1.42 x 1.35 x 1.28) - 1 = 145.95% and correctly concluded the
   subsidiary's economy is highly inflationary.
2. It correctly applied the remeasurement method and correctly routed the
   remeasurement loss to **net income rather than OCI** -- i.e. it did
   *not* fall for the `assumption_violation` trap the task is built to
   probe.
3. It then **added** the $85,000 remeasurement loss instead of
   subtracting it: $510,000 + $85,000 = $595,000, where the oracle is
   $510,000 - $85,000 = $425,000.

The error is a sign flip on the final line, not a misunderstanding of
ASC 830. Under the current verifier this is indistinguishable from a
model that routed the loss to OCI, ignored the inflation threshold
entirely, or otherwise missed the mechanism -- all of them simply
register as "not within 1% of 425000."

This matters for the paper's central claim. The FX task's pass rate is
presented as evidence about `assumption_violation` susceptibility, but
2 of 2 observed Haiku failures are *not* assumption violations. Taken at
face value the aggregate figure overstates the failure family's
incidence, and the direction of the bias is unknown in general: a sign
error could equally mask a conceptual failure that happens to land on a
passing number.

### Suggested future verifier revision (not implemented)

Detect the signature algebraically rather than by reading completions. A
sign flip on a subtracted component leaves the result exactly
`2 x component` above the expected value, so a check of the form

    abs(extracted - (expected + 2 * loss_amount)) <= tolerance

would classify $595,000 as a distinct `sign_error` category rather than a
generic failure. This generalizes to any task with a signed component
(the pension task's `expected_return` term has the same property).

Deliberately **not** fixed now: changing the verifier mid-study would
make these results non-comparable with the runs already recorded, and
the correct scope -- whether `sign_error` counts as a pass, a fail, or an
excluded trial -- is a study-design decision, not an implementation
detail. Recording it here so the limitation is disclosed rather than
silently carried into the results.
