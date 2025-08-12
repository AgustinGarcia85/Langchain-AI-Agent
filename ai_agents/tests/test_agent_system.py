import os
import re

import pytest

# Ensure imports resolve when running from repo root
import sys
sys.path.append("/workspace")

from ai_agents.agent_system import Orchestrator, get_shared_memory  # noqa: E402


def test_memory_initialization():
    memory = get_shared_memory()
    assert memory is not None


def test_orchestrator_example_flow():
    # Ensure tests do not require real OpenAI/Daytona
    os.environ.pop("OPENAI_API_KEY", None)
    os.environ.pop("DAYTONA_API_KEY", None)
    os.environ.pop("DAYTONA_SERVER_URL", None)

    orch = Orchestrator()
    out = orch.run("Fetch the current date and list files.")

    # Final output should include our deterministic command labels
    assert "Command: date" in out
    assert "Command: ls -la" in out

    # It should include some stdout content (date output varies; just check non-empty after STDOUT label appears at least once)
    assert "STDOUT:" in out


@pytest.mark.parametrize("task,expected_cmds", [
    ("just show me date", ["date"]),
    ("list files", ["ls -la"]),
])
def test_orchestrator_planner_fallback(task, expected_cmds):
    os.environ.pop("OPENAI_API_KEY", None)
    orch = Orchestrator()
    final = orch.run(task)
    for cmd in expected_cmds:
        assert f"Command: {cmd}" in final