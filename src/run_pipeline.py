"""
End-to-end pipeline runner.

    python3 src/run_pipeline.py --provider mock
    python3 src/run_pipeline.py --provider anthropic --model claude-sonnet-4-6
    python3 src/run_pipeline.py --provider anthropic --trials 5
    python3 src/run_pipeline.py --provider openai --model gpt-5
    python3 src/run_pipeline.py --provider gemini --model gemini-2.5-pro

Loads every task in data/tasks/, runs each configured model against
every task `--trials` times (default 1), scores each response against
the oracle answer, tags each result by failure family, and writes CSV
tables + PNG figures to data/results/ and figures/.

A single trial (the default) tells you almost nothing about whether a
model reliably solves a task -- one completion could be a fluke either
way. Use --trials 5 (or more) once you're deciding whether a task
needs hardening, so the pass rate in pass_rate_by_task.csv is an
actual proportion with a meaningful confidence interval, not a single
0-or-1 coin flip.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from task_loader import load_all_tasks
from model_runner import AnthropicClient, GeminiClient, MockClient, OpenAIClient, run_all
from verifier import score
from failure_tagger import tag_result
from stats_report import build_report


def build_clients(provider: str, model: str | None) -> list:
    if provider == "mock":
        return [MockClient()]
    if provider == "anthropic":
        return [AnthropicClient(model=model or "claude-sonnet-4-6")]
    if provider == "openai":
        return [OpenAIClient(model=model or "gpt-5")]
    if provider == "gemini":
        return [GeminiClient(model=model or "gemini-2.5-pro")]
    raise ValueError(f"Unknown provider: {provider}")


def main():
    parser = argparse.ArgumentParser(description="Run the adversarial eval pipeline")
    parser.add_argument("--provider", default="mock",
                         choices=["mock", "anthropic", "openai", "gemini"])
    parser.add_argument("--model", default=None,
                         help="Override the default model name for the chosen provider")
    parser.add_argument("--trials", type=int, default=1,
                         help="Number of independent completions per (task, model) pair. "
                              "Use >1 to get a real pass rate instead of a single "
                              "0-or-1 result. Each trial is a separate API call, so cost "
                              "scales linearly with this value.")
    args = parser.parse_args()

    if args.trials < 1:
        parser.error("--trials must be >= 1")

    repo_root = Path(__file__).resolve().parent.parent
    tasks_dir = repo_root / "data" / "tasks"
    results_dir = repo_root / "data" / "results"

    tasks = load_all_tasks(tasks_dir)
    print(f"Loaded {len(tasks)} tasks from {tasks_dir}")

    clients = build_clients(args.provider, args.model)
    n_calls = len(tasks) * len(clients) * args.trials
    print(f"Running {len(clients)} model(s): {[c.name for c in clients]} "
          f"x {args.trials} trial(s) = {n_calls} API call(s)")

    run_results = run_all(tasks, clients, results_dir, trials=args.trials)

    tasks_by_id = {t.task_id: t for t in tasks}
    tagged = []
    scored_rows = []
    for r in run_results:
        task = tasks_by_id[r.task_id]
        scored = score(task, r.raw_response, r.model_name)
        tagged.append(tag_result(task, scored, trial=r.trial))
        scored_rows.append({
            "task_id": scored.task_id,
            "model_name": scored.model_name,
            "trial": r.trial,
            "extracted_answer": scored.extracted_answer,
            "expected_answer": scored.expected_answer,
            "passed": scored.passed,
            "parse_error": scored.parse_error,
            "run_error": r.error,
        })

    scored_path = results_dir / "scored_results.json"
    scored_path.write_text(json.dumps(scored_rows, indent=2), encoding="utf-8")
    print(f"\nWrote per-task scored results to {scored_path}")

    build_report(tagged, repo_root)
    print(f"\nFigures written to {repo_root / 'figures'}")
    print(f"Tables written to {results_dir}")


if __name__ == "__main__":
    main()
