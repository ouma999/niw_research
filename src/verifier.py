"""
Scores a model's raw completion against a task's oracle answer.

Currently supports numeric answers extracted from a "FINAL ANSWER: <n>"
line, matching the output format every instruction.md in this repo
requires. Extend `extract_numeric_answer` if you add tasks with a
different answer format (e.g. multiple choice, structured JSON).
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from task_loader import Task


@dataclass
class ScoredResult:
    task_id: str
    model_name: str
    extracted_answer: float | None
    expected_answer: float
    passed: bool
    parse_error: bool


FINAL_ANSWER_RE = re.compile(
    r"FINAL ANSWER:\s*\$?\s*(-?[\d,]*\.?\d+)", re.IGNORECASE
)


def extract_numeric_answer(raw_response: str) -> float | None:
    match = FINAL_ANSWER_RE.search(raw_response)
    if not match:
        return None
    cleaned = match.group(1).replace(",", "")
    try:
        return float(cleaned)
    except ValueError:
        return None


def score(task: Task, raw_response: str, model_name: str) -> ScoredResult:
    extracted = extract_numeric_answer(raw_response)
    if extracted is None:
        return ScoredResult(
            task_id=task.task_id,
            model_name=model_name,
            extracted_answer=None,
            expected_answer=float(task.answer),
            passed=False,
            parse_error=True,
        )

    expected = float(task.answer)
    tolerance = task.tolerance_pct / 100.0
    passed = abs(extracted - expected) / abs(expected) <= tolerance

    return ScoredResult(
        task_id=task.task_id,
        model_name=model_name,
        extracted_answer=extracted,
        expected_answer=expected,
        passed=passed,
        parse_error=False,
    )


if __name__ == "__main__":
    from pathlib import Path
    from task_loader import load_all_tasks

    root = Path(__file__).resolve().parent.parent
    tasks = {t.task_id: t for t in load_all_tasks(root / "data" / "tasks")}

    demo_response = "The full derivation gives...\n\nFINAL ANSWER: 350000"
    task = tasks["demo_pension_restatement"]
    result = score(task, demo_response, "demo-model")
    print(result)
