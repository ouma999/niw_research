"""
Pluggable model clients + a runner that sends each task's instruction to
each configured model and saves the raw completion to data/results/.

Supported clients:
  - AnthropicClient  : real API calls to api.anthropic.com (needs
                        ANTHROPIC_API_KEY in the environment)
  - OpenAIClient      : real API calls to OpenAI (needs OPENAI_API_KEY;
                        note this domain is not reachable from every
                        sandboxed environment -- run this from your own
                        machine/CI if it's blocked)
  - MockClient        : deterministic offline stand-in, used for
                        pipeline testing without any API key or network
                        access. Useful for CI and for proving the
                        harness works before spending API budget.

Add a new provider by subclassing ModelClient and implementing
`complete(self, prompt: str) -> str`.
"""
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path

import requests

from task_loader import Task


class ModelClient:
    name: str = "base"

    def complete(self, prompt: str) -> str:
        raise NotImplementedError


class AnthropicClient(ModelClient):
    def __init__(self, model: str = "claude-sonnet-4-6", max_tokens: int = 4096):
        self.name = model
        self.model = model
        self.max_tokens = max_tokens
        self.api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY is not set. Export it before running "
                "real evaluations, e.g.:\n"
                "  export ANTHROPIC_API_KEY=sk-ant-..."
            )

    def complete(self, prompt: str) -> str:
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": self.model,
                "max_tokens": self.max_tokens,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=120,
        )
        resp.raise_for_status()
        data = resp.json()
        return "".join(
            block.get("text", "") for block in data.get("content", [])
            if block.get("type") == "text"
        )


class OpenAIClient(ModelClient):
    def __init__(self, model: str = "gpt-5", max_tokens: int = 4096):
        self.name = model
        self.model = model
        self.max_tokens = max_tokens
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is not set. Export it before running "
                "real evaluations."
            )

    def complete(self, prompt: str) -> str:
        resp = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "max_completion_tokens": self.max_tokens,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=120,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]


class GeminiClient(ModelClient):
    def __init__(self, model: str = "gemini-2.5-pro", max_tokens: int = 4096):
        self.name = model
        self.model = model
        self.max_tokens = max_tokens
        self.api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise RuntimeError(
                "GOOGLE_API_KEY (or GEMINI_API_KEY) is not set. Export it "
                "before running real evaluations, e.g.:\n"
                "  export GOOGLE_API_KEY=AIza..."
            )

    def complete(self, prompt: str) -> str:
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:generateContent"
        )
        resp = requests.post(
            url,
            headers={
                "x-goog-api-key": self.api_key,
                "Content-Type": "application/json",
            },
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"maxOutputTokens": self.max_tokens},
            },
            timeout=120,
        )
        resp.raise_for_status()
        data = resp.json()
        candidates = data.get("candidates", [])
        if not candidates:
            return ""
        parts = candidates[0].get("content", {}).get("parts", [])
        return "".join(p.get("text", "") for p in parts)


class MockClient(ModelClient):
    """
    Deterministic OFFLINE stand-in with no reasoning ability. It exists
    only to prove the runner/verifier/stats wiring works end to end
    without spending API budget or requiring network access. It does
    NOT produce meaningful accuracy numbers -- do not use its output in
    any real results table or figure. Swap in AnthropicClient/
    OpenAIClient for real evaluation runs.
    """

    def __init__(self, name: str = "mock-smoke-test-model"):
        self.name = name

    def complete(self, prompt: str) -> str:
        import re

        # Grabs the first plausible number in the prompt as a stand-in
        # answer, just so downstream parsing/scoring has something to
        # operate on during a smoke test.
        numbers = re.findall(r"[\$]?([\d,]+\.\d{2}|\d{3,})", prompt)
        candidate = numbers[0].replace(",", "") if numbers else "0"
        return f"Based on the facts above, the calculation yields:\n\nFINAL ANSWER: {candidate}"


CLIENT_REGISTRY = {
    "anthropic": AnthropicClient,
    "openai": OpenAIClient,
    "gemini": GeminiClient,
    "mock": MockClient,
}


@dataclass
class RunResult:
    task_id: str
    model_name: str
    raw_response: str
    latency_sec: float
    trial: int = 0
    error: str | None = None


def run_model_on_task(client: ModelClient, task: Task, trial: int = 0) -> RunResult:
    start = time.time()
    try:
        response = client.complete(task.instruction)
        error = None
    except Exception as exc:  # noqa: BLE001
        response = ""
        error = str(exc)
    latency = time.time() - start
    return RunResult(
        task_id=task.task_id,
        model_name=client.name,
        raw_response=response,
        latency_sec=latency,
        trial=trial,
        error=error,
    )


def run_all(
    tasks: list[Task],
    clients: list[ModelClient],
    results_dir: Path,
    trials: int = 1,
) -> list[RunResult]:
    """
    Runs every (task, client) pair `trials` times. Since LLM APIs are
    not deterministic even at temperature 0 in practice, running a
    single trial per task tells you almost nothing about a model's
    real pass rate on that task -- one lucky or unlucky completion
    looks identical to a stable result. `trials > 1` is what turns a
    single 0-or-1 data point into an actual proportion with a
    meaningful confidence interval (see stats_report.wilson_interval).
    """
    results_dir = Path(results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)
    all_results = []
    for task in tasks:
        for client in clients:
            for trial in range(trials):
                result = run_model_on_task(client, task, trial=trial)
                all_results.append(result)
                suffix = f"__trial{trial}" if trials > 1 else ""
                out_path = results_dir / f"{task.task_id}__{client.name}{suffix}.json"
                out_path.write_text(json.dumps({
                    "task_id": result.task_id,
                    "model_name": result.model_name,
                    "trial": result.trial,
                    "raw_response": result.raw_response,
                    "latency_sec": result.latency_sec,
                    "error": result.error,
                }, indent=2), encoding="utf-8")
    return all_results


if __name__ == "__main__":
    from task_loader import load_all_tasks

    root = Path(__file__).resolve().parent.parent
    tasks = load_all_tasks(root / "data" / "tasks")
    clients = [MockClient()]
    results = run_all(tasks, clients, root / "data" / "results")
    for r in results:
        print(f"{r.task_id:30s} {r.model_name:20s} -> {r.raw_response[:60]!r}")
