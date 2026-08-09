"""
Loads task directories (task.toml + instruction.md) into a uniform
in-memory schema the rest of the pipeline can work with.

Expected layout, one directory per task:

    data/tasks/<task_id>/
        task.toml
        instruction.md
        solution/solve.py
        tests/test_outputs.py

This mirrors the Dynamo platform's task layout so real task exports can
be dropped in with minimal reshaping.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover
    import tomli as tomllib  # type: ignore


@dataclass
class Task:
    task_id: str
    domain: str
    title: str
    difficulty: str
    failure_family: str
    failure_family_name: str
    instruction: str
    answer_type: str
    answer: float | str
    tolerance_pct: float
    category: str = ""
    subcategory: str = ""
    path: Path = field(default=None, repr=False)


def load_task(task_dir: Path) -> Task:
    task_dir = Path(task_dir)
    toml_path = task_dir / "task.toml"
    instruction_path = task_dir / "instruction.md"

    with open(toml_path, "rb") as f:
        cfg = tomllib.load(f)

    instruction = instruction_path.read_text(encoding="utf-8")

    task_cfg = cfg["task"]
    oracle_cfg = cfg["oracle"]
    meta_cfg = cfg.get("metadata", {})

    return Task(
        task_id=task_cfg["id"],
        domain=task_cfg["domain"],
        title=task_cfg["title"],
        difficulty=task_cfg["difficulty"],
        failure_family=task_cfg["failure_family"],
        failure_family_name=task_cfg.get("failure_family_name", ""),
        instruction=instruction,
        answer_type=oracle_cfg["answer_type"],
        answer=oracle_cfg["answer"],
        tolerance_pct=float(oracle_cfg.get("tolerance_pct", 1.0)),
        category=meta_cfg.get("category", ""),
        subcategory=meta_cfg.get("subcategory", ""),
        path=task_dir,
    )


def load_all_tasks(tasks_root: Path) -> list[Task]:
    tasks_root = Path(tasks_root)
    tasks = []
    for child in sorted(tasks_root.iterdir()):
        if child.is_dir() and (child / "task.toml").exists():
            tasks.append(load_task(child))
    return tasks


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent / "data" / "tasks"
    for t in load_all_tasks(root):
        print(f"{t.task_id:30s} domain={t.domain:25s} "
              f"family={t.failure_family} ({t.failure_family_name})")
