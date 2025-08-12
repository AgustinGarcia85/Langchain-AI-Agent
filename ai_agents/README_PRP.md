## PRP: LangChain + Daytona Agent with Memory and Orchestration

### Overview
This module provides a modular agent system where:
- Planner breaks down tasks into shell steps
- Executor runs steps in a Daytona sandbox (with local fallback)
- Reviewer validates outputs
- Orchestrator coordinates and compiles a final response

All agents share memory via `ConversationBufferMemory`. Secrets are loaded from `.env`.

### Install
```bash
pip install -r requirements.txt
```

### Configure
Copy `.env.example` to `.env` and set values:
```env
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4o-mini
DAYTONA_API_KEY=your-daytona-api-key
DAYTONA_SERVER_URL=https://your-daytona-server
```
If Daytona vars are not set, a safe local, ephemeral sandbox is used.

### Run Example
```bash
python agent_system.py
```

### Usage in Code
```python
from ai_agents.agent_system import Orchestrator
orch = Orchestrator()
print(orch.run("Fetch the current date and list files."))
```

### Tests
```bash
pytest -q
```

### Notes
- Uses `langchain_openai.ChatOpenAI` when `OPENAI_API_KEY` is set; otherwise falls back to deterministic planning for offline tests.
- Daytona SDK is optional at runtime; when configured, it will be preferred for sandboxed execution.