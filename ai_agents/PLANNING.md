# PLANNING.md

## Project: AI Agents with Langchain & LangSmith

### Purpose
Develop modular, robust, and scalable AI agents leveraging the latest LangChain (core, text splitters, community, LangGraph, OpenAI integrations) for agent orchestration, and LangSmith for observability, debugging, and evaluation.

### Architecture
- Modular agent design: Each agent is a self-contained module.
- Use LangChain for chaining, memory, tool integrations, and RAG workflows (see latest docs for vector stores, text splitters, and prompt templates).
- Use LangGraph for building agentic workflows as graphs.
- Use LangSmith for experiment tracking, debugging, and evaluation (enable tracing via environment variables).
- Virtual environment managed by UV for reproducibility.
- Streamlit UI for agent interaction.

### Tech Stack
- Python 3.12+
- langchain (core)
- langchain-text-splitters
- langchain-community
- langchain-openai
- langgraph
- langsmith
- streamlit
- dotenv
- UV (for dependency management)

### Constraints
- Keep each module under 500 lines; split logic as needed.
- Prioritize security, error handling, and test coverage.
- Avoid magic numbers; use named constants.
- Modular, reusable, and maintainable code.

### Tools
- Langchain
- LangSmith
- Streamlit
- UV

### Next Steps
- Define agent interface and base class.
- Implement a sample agent (React agent with Streamlit UI).
- Integrate LangSmith for observability.
- Write unit tests for all modules.
