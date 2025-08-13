from __future__ import annotations

import os
import shlex
import subprocess
import tempfile
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, TYPE_CHECKING

from dotenv import load_dotenv

if TYPE_CHECKING:
    from langchain_openai import ChatOpenAI

# LangChain (modern imports)
try:
    from langchain_openai import ChatOpenAI
except Exception:  # pragma: no cover - optional at runtime
    ChatOpenAI = None  # type: ignore

# Attempt to import Daytona SDK
try:
    from daytona import Daytona, DaytonaConfig  # type: ignore
except Exception:  # pragma: no cover - SDK optional for tests
    Daytona = None  # type: ignore
    DaytonaConfig = None  # type: ignore


# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
DAYTONA_API_KEY = os.getenv("DAYTONA_API_KEY", "")
DAYTONA_SERVER_URL = os.getenv("DAYTONA_SERVER_URL", "")


@dataclass
class SimpleMemory:
    """Simple conversation memory to replace deprecated ConversationBufferMemory"""
    conversations: List[dict] = field(default_factory=list)
    
    def save_context(self, inputs: dict, outputs: dict) -> None:
        """Save a conversation turn to memory"""
        self.conversations.append({
            "input": inputs.get("input", ""),
            "output": outputs.get("output", "")
        })
    
    def get_conversation_history(self) -> str:
        """Get conversation history as a formatted string"""
        history = []
        for conv in self.conversations:
            if conv["input"]:
                history.append(f"Input: {conv['input']}")
            if conv["output"]:
                history.append(f"Output: {conv['output']}")
        return "\n".join(history)


def get_shared_memory() -> SimpleMemory:
    """Get a shared memory instance"""
    return SimpleMemory()


@dataclass
class ExecutionResult:
    command: str
    exit_code: int
    stdout: str
    stderr: str


class SandboxExecutor:
    """Executes shell commands in an isolated environment.

    Prefers Daytona SDK when available/configured; otherwise falls back
    to a local, ephemeral temp directory using subprocess.
    """

    def __init__(self) -> None:
        self._use_daytona = False
        self._daytona_client = None

        if Daytona and DAYTONA_API_KEY and DAYTONA_SERVER_URL:
            try:
                config = DaytonaConfig(api_key=DAYTONA_API_KEY, server_url=DAYTONA_SERVER_URL)  # type: ignore
                self._daytona_client = Daytona(config=config)  # type: ignore
                # Heuristic: mark as usable. Actual execution API may differ by SDK version.
                self._use_daytona = hasattr(self._daytona_client, "execute")
            except Exception:
                # Fallback to local if Daytona init fails
                self._use_daytona = False
                self._daytona_client = None

    def execute(self, command: str) -> ExecutionResult:
        if self._use_daytona and self._daytona_client is not None:
            # NOTE: This assumes Daytona SDK exposes an `execute` method.
            # If your SDK differs, adjust here accordingly.
            try:
                result = self._daytona_client.execute(command)  # type: ignore[attr-defined]
                # Normalize result into ExecutionResult
                stdout = getattr(result, "stdout", "") if result is not None else ""
                stderr = getattr(result, "stderr", "") if result is not None else ""
                code = getattr(result, "exit_code", 0) if result is not None else 0
                return ExecutionResult(command=command, exit_code=int(code), stdout=str(stdout), stderr=str(stderr))
            except Exception as exec_err:
                return ExecutionResult(command=command, exit_code=1, stdout="", stderr=str(exec_err))

        # Local fallback: run in temp dir for isolation
        with tempfile.TemporaryDirectory(prefix="sandbox-") as tmpdir:
            process = subprocess.run(
                ["bash", "-lc", command],
                cwd=tmpdir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            return ExecutionResult(
                command=command,
                exit_code=process.returncode,
                stdout=process.stdout,
                stderr=process.stderr,
            )


def _make_llm():
    if not OPENAI_API_KEY or ChatOpenAI is None:
        return None
    # Use a lightweight model if available
    return ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"), temperature=0)


def _plan_with_llm(llm, task: str) -> str:
    system = (
        "You are a planner that converts a user task into a minimal, safe list of bash commands.\n"
        "Rules:\n"
        "- Output ONLY the commands, one per line.\n"
        "- No explanations or numbering.\n"
        "- Prefer portable commands (date, ls).\n"
        "- Never use destructive commands."
    )
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": f"Task: {task}"},
    ]
    resp = llm.invoke(messages)  # type: ignore[attr-defined]
    return getattr(resp, "content", str(resp))


def _review_with_llm(llm, output: ExecutionResult) -> str:
    system = (
        "You are a reviewer. Assess if the command output indicates success.\n"
        "Respond concisely with a 1-2 sentence verdict."
    )
    content = (
        f"Command: {output.command}\nExit: {output.exit_code}\nSTDOUT:\n{output.stdout}\nSTDERR:\n{output.stderr}"
    )
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": content},
    ]
    resp = llm.invoke(messages)  # type: ignore[attr-defined]
    return getattr(resp, "content", str(resp))


class PlannerAgent:
    def __init__(self, memory: SimpleMemory, llm):
        self.memory = memory
        self.llm = llm

    def run(self, task: str) -> List[str]:
        if self.llm is not None:
            plan_text = _plan_with_llm(self.llm, task)
        else:
            # Offline fallback plan heuristic
            plan_text = "date\nls -la"

        self.memory.save_context({"input": f"[planner]\n{plan_text}"}, {"output": ""})
        steps = [line.strip() for line in plan_text.splitlines() if line.strip()]
        return steps


class ExecutorAgent:
    def __init__(self, memory: SimpleMemory, executor: SandboxExecutor) -> None:
        self.memory = memory
        self.executor = executor

    def run(self, command: str) -> ExecutionResult:
        # Basic safety: prevent obviously dangerous commands in fallback mode
        forbidden = {"rm -rf /", ":(){ :|:& };:"}
        lowered = command.strip().lower()
        if any(f in lowered for f in forbidden):
            result = ExecutionResult(command=command, exit_code=1, stdout="", stderr="Forbidden command")
        else:
            result = self.executor.execute(command)

        self.memory.save_context(
            {"input": f"[executor]\n$ {command}"},
            {"output": f"EXIT {result.exit_code}\n{result.stdout}{result.stderr}"},
        )
        return result


class ReviewerAgent:
    def __init__(self, memory: SimpleMemory, llm):
        self.memory = memory
        self.llm = llm

    def run(self, output: ExecutionResult) -> str:
        if self.llm is not None:
            review_text = _review_with_llm(self.llm, output)
        else:
            if output.exit_code == 0 and output.stderr.strip() == "":
                review_text = "Execution succeeded."
            else:
                review_text = f"Execution may have issues. Exit {output.exit_code}."

        self.memory.save_context({"input": "[reviewer]"}, {"output": review_text})
        return review_text


class Orchestrator:
    def __init__(self, memory=None, llm=None):
        self.memory = memory or get_shared_memory()
        self.llm = llm if llm is not None else _make_llm()
        self.executor = SandboxExecutor()
        self.planner = PlannerAgent(self.memory, self.llm)
        self.runner = ExecutorAgent(self.memory, self.executor)
        self.reviewer = ReviewerAgent(self.memory, self.llm)

    def run(self, task: str) -> str:
        steps = self.planner.run(task)
        results: List[Tuple[str, ExecutionResult, str]] = []

        for step in steps:
            if not step:
                continue
            exec_result = self.runner.run(step)
            review = self.reviewer.run(exec_result)
            results.append((step, exec_result, review))

        # Compile final coherent output
        final_lines: List[str] = ["Final Result"]
        final_lines.append(f"Task: {task}")
        final_lines.append("")
        for step, exec_result, review in results:
            final_lines.append(f"Command: {step}")
            final_lines.append(f"Exit Code: {exec_result.exit_code}")
            if exec_result.stdout.strip():
                final_lines.append("STDOUT:")
                final_lines.append(exec_result.stdout.strip())
            if exec_result.stderr.strip():
                final_lines.append("STDERR:")
                final_lines.append(exec_result.stderr.strip())
            final_lines.append(f"Review: {review}")
            final_lines.append("")

        final_text = "\n".join(final_lines).strip()
        self.memory.save_context({"input": "[orchestrator]"}, {"output": final_text})
        return final_text


def run_example() -> str:
    orchestrator = Orchestrator()
    return orchestrator.run("Fetch the current date and list files.")


if __name__ == "__main__":
    print(run_example())