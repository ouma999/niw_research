"""
Tags each scored result with the task's failure mechanism (per the
descriptive taxonomy in the accompanying paper) so results can be
aggregated by *why* a model failed, not just whether it failed.

Failure mechanism reference:
  reflex_override             - a trained professional reflex produces
      the wrong answer; correct approach needs one non-obvious
      derivation step.
  heuristic_substitution       - a shortcut looks like the correct
      method but silently diverges from it.
  distractor_injection         - a distractor resource or datum
      invites misuse.
  evidence_synthesis_gap       - the answer must be inferred from
      partial evidence, not read off directly.
  assumption_violation         - an assumption that normally holds is
      violated in this instance.
  weak_signal_fusion           - failure only shows up when multiple
      weak signals are combined.
  exhaustive_coverage_failure  - many sub-parts must all be correct
      simultaneously.
  temporal_coupling            - order-of-operations or history
      dependence changes the answer.
  staleness_error               - using a stale value instead of the
      value as of the relevant date.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from task_loader import Task
from verifier import ScoredResult


@dataclass
class TaggedResult:
    task_id: str
    model_name: str
    domain: str
    failure_family: str
    failure_family_name: str
    passed: bool
    parse_error: bool
    trial: int = 0


def tag_result(task: Task, scored: ScoredResult, trial: int = 0) -> TaggedResult:
    return TaggedResult(
        task_id=task.task_id,
        model_name=scored.model_name,
        domain=task.domain,
        failure_family=task.failure_family,
        failure_family_name=task.failure_family_name,
        passed=scored.passed,
        parse_error=scored.parse_error,
        trial=trial,
    )


def aggregate_by_family(tagged: list[TaggedResult]) -> dict[str, dict[str, int]]:
    """Returns {failure_family: {"pass": n, "fail": n, "total": n}}"""
    agg: dict[str, dict[str, int]] = defaultdict(lambda: {"pass": 0, "fail": 0, "total": 0})
    for t in tagged:
        agg[t.failure_family]["total"] += 1
        agg[t.failure_family]["pass" if t.passed else "fail"] += 1
    return dict(agg)


def aggregate_by_model(tagged: list[TaggedResult]) -> dict[str, dict[str, int]]:
    agg: dict[str, dict[str, int]] = defaultdict(lambda: {"pass": 0, "fail": 0, "total": 0})
    for t in tagged:
        agg[t.model_name]["total"] += 1
        agg[t.model_name]["pass" if t.passed else "fail"] += 1
    return dict(agg)


def aggregate_by_model_and_family(
    tagged: list[TaggedResult],
) -> dict[tuple[str, str], dict[str, int]]:
    agg: dict[tuple[str, str], dict[str, int]] = defaultdict(
        lambda: {"pass": 0, "fail": 0, "total": 0}
    )
    for t in tagged:
        key = (t.model_name, t.failure_family)
        agg[key]["total"] += 1
        agg[key]["pass" if t.passed else "fail"] += 1
    return dict(agg)


def aggregate_by_task(tagged: list[TaggedResult]) -> dict[str, dict[str, int]]:
    """
    Returns {task_id: {"pass": n, "fail": n, "total": n}}, i.e. the
    per-task pass rate across all trials and models. This is what
    tells you whether a specific task is actually discriminating
    (e.g. 1/5 solved) or has been solved cleanly (e.g. 5/5) and needs
    hardening before it's a useful adversarial item.
    """
    agg: dict[str, dict[str, int]] = defaultdict(lambda: {"pass": 0, "fail": 0, "total": 0})
    for t in tagged:
        agg[t.task_id]["total"] += 1
        agg[t.task_id]["pass" if t.passed else "fail"] += 1
    return dict(agg)


def aggregate_by_task_and_model(
    tagged: list[TaggedResult],
) -> dict[tuple[str, str], dict[str, int]]:
    """Per-task pass rate broken out by model, across trials."""
    agg: dict[tuple[str, str], dict[str, int]] = defaultdict(
        lambda: {"pass": 0, "fail": 0, "total": 0}
    )
    for t in tagged:
        key = (t.task_id, t.model_name)
        agg[key]["total"] += 1
        agg[key]["pass" if t.passed else "fail"] += 1
    return dict(agg)
