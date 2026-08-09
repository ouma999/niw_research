"""
Aggregate scored/tagged results into the tables and figures the paper
needs: pass rate by model, pass rate by failure family, and a
model x failure-family breakdown, each with Wilson score confidence
intervals (appropriate for small-sample binomial proportions, unlike
a naive normal-approximation CI).
"""
from __future__ import annotations

import csv
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from failure_tagger import TaggedResult


def wilson_interval(successes: int, total: int, z: float = 1.96) -> tuple[float, float, float]:
    """Returns (point_estimate, lower_bound, upper_bound) for a binomial
    proportion using the Wilson score interval. Well-behaved for small
    n and for proportions near 0 or 1, unlike the normal approximation.
    """
    if total == 0:
        return (0.0, 0.0, 0.0)
    p_hat = successes / total
    denom = 1 + z**2 / total
    center = (p_hat + z**2 / (2 * total)) / denom
    margin = (
        z * math.sqrt((p_hat * (1 - p_hat) + z**2 / (4 * total)) / total)
    ) / denom
    return (p_hat, max(0.0, center - margin), min(1.0, center + margin))


def pass_rate_table(agg: dict, label: str = "group") -> list[dict]:
    rows = []
    for key, counts in sorted(agg.items()):
        p_hat, lo, hi = wilson_interval(counts["pass"], counts["total"])
        rows.append({
            label: key,
            "n": counts["total"],
            "pass": counts["pass"],
            "fail": counts["fail"],
            "pass_rate": round(p_hat, 4),
            "ci_low": round(lo, 4),
            "ci_high": round(hi, 4),
        })
    return rows


def write_csv(rows: list[dict], out_path: Path) -> None:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        out_path.write_text("")
        return
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def plot_pass_rate_by_group(rows: list[dict], label: str, title: str, out_path: Path) -> None:
    labels = [str(r[label]) for r in rows]
    rates = [r["pass_rate"] * 100 for r in rows]
    err_low = [(r["pass_rate"] - r["ci_low"]) * 100 for r in rows]
    err_high = [(r["ci_high"] - r["pass_rate"]) * 100 for r in rows]

    fig, ax = plt.subplots(figsize=(7, 4.2))
    bars = ax.bar(labels, rates, yerr=[err_low, err_high], capsize=4,
                   color="#2F5D8A", alpha=0.85)
    ax.set_ylabel("Pass rate (%)")
    ax.set_ylim(0, 100)
    ax.set_title(title)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    for bar, r in zip(bars, rows):
        ax.annotate(f"n={r['n']}", (bar.get_x() + bar.get_width() / 2, 2),
                    ha="center", fontsize=8, color="white")
    plt.xticks(rotation=20, ha="right")
    fig.tight_layout()
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def build_report(tagged: list[TaggedResult], out_dir: Path) -> None:
    from failure_tagger import (
        aggregate_by_family,
        aggregate_by_model,
        aggregate_by_task_and_model,
    )

    out_dir = Path(out_dir)

    by_model = pass_rate_table(aggregate_by_model(tagged), label="model")
    by_family = pass_rate_table(aggregate_by_family(tagged), label="failure_family")

    # Per-task-and-model table: the key output once trials > 1. Row
    # labels combine task and model so a task tested against multiple
    # models is easy to scan (e.g. "demo_pension_restatement | claude-sonnet-4-6").
    by_task_model_raw = aggregate_by_task_and_model(tagged)
    by_task_model = pass_rate_table(
        {f"{task_id} | {model}": counts for (task_id, model), counts in by_task_model_raw.items()},
        label="task_and_model",
    )

    write_csv(by_model, out_dir / "data" / "results" / "pass_rate_by_model.csv")
    write_csv(by_family, out_dir / "data" / "results" / "pass_rate_by_family.csv")
    write_csv(by_task_model, out_dir / "data" / "results" / "pass_rate_by_task.csv")

    plot_pass_rate_by_group(
        by_model, "model", "Pass rate by model",
        out_dir / "figures" / "pass_rate_by_model.png",
    )
    plot_pass_rate_by_group(
        by_family, "failure_family", "Pass rate by failure family",
        out_dir / "figures" / "pass_rate_by_family.png",
    )
    if by_task_model:
        plot_pass_rate_by_group(
            by_task_model, "task_and_model", "Pass rate by task",
            out_dir / "figures" / "pass_rate_by_task.png",
        )

    print("\n=== Pass rate by model ===")
    for r in by_model:
        print(f"  {r['model']:25s} {r['pass']}/{r['n']}  "
              f"({r['pass_rate']:.0%}, 95% CI [{r['ci_low']:.0%}, {r['ci_high']:.0%}])")

    print("\n=== Pass rate by failure family ===")
    for r in by_family:
        print(f"  {r['failure_family']:5s} {r['pass']}/{r['n']}  "
              f"({r['pass_rate']:.0%}, 95% CI [{r['ci_low']:.0%}, {r['ci_high']:.0%}])")

    print("\n=== Pass rate by task ===")
    for r in by_task_model:
        print(f"  {r['task_and_model']:60s} {r['pass']}/{r['n']}  "
              f"({r['pass_rate']:.0%}, 95% CI [{r['ci_low']:.0%}, {r['ci_high']:.0%}])")
