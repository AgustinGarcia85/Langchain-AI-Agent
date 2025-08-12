# AI Agents Repository

This repository contains multiple AI agent implementations using LangChain and various tools for different use cases.

## 🚀 Available Agents

### 1. React Agent (LangChain + LangSmith)
A web-search-enabled AI assistant using the LangChain ReAct agent framework, Streamlit for the UI, and LangSmith for tracing and observability.

**Features:**
- Web search via Brave Search API
- Conversational interface powered by Streamlit
- LangSmith tracing for agent runs
- Secure environment variable management

**Run with:**
```bash
streamlit run react_agent.py
```

### 2. PRP: LangChain + Daytona Agent System 🆕
A modular AI agent system that provides safe, coordinated execution of tasks using isolated sandboxes with shared memory and intelligent orchestration.

**Features:**
- **🤖 Planner Agent**: Breaks down complex tasks into executable steps
- **⚡ Executor Agent**: Safely executes commands in Daytona sandbox
- **🔍 Reviewer Agent**: Validates and reviews execution outputs
- **🎯 Orchestrator**: Coordinates all agents and compiles final responses
- **Safe Execution**: All code runs in isolated Daytona sandboxes
- **Shared Memory**: Agents maintain conversation history across interactions
- **Intelligent Planning**: AI-powered task breakdown and optimization
- **Quality Assurance**: Automated review and validation of all outputs

**Run with:**
```bash
# Basic usage
python agent_system.py

# Interactive demo
python demo.py

# Run tests
python test_agent_system.py
```

## 🛠️ Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Configuration
Create a `.env` file in the `ai_agents` directory:

**For React Agent:**
```env
OPENAI_API_KEY=your-openai-key
LANGSMITH_API_KEY=your-langsmith-key
BRAVE_SEARCH_API_KEY=your-brave-search-key
```

**For PRP Agent System:**
```env
OPENAI_API_KEY=your-openai-key
DAYTONA_API_KEY=your-daytona-key
DAYTONA_SERVER_URL=https://api.daytona.io
```

**Copy from example:**
```bash
cp .env.example .env
# Then edit with your actual API keys
```

## 📚 Documentation

- **React Agent**: See inline code comments and docstrings
- **PRP Agent System**: See `AGENT_SYSTEM_README.md` for comprehensive documentation
- **Configuration**: See `config.py` for customizable settings

## 🔒 Security

- **Never commit your `.env` file.** It is excluded via `.gitignore`.
- API keys are loaded securely from environment variables.
- Daytona sandbox provides isolated execution environment.

## 🧪 Testing

```bash
# Test the PRP agent system
python test_agent_system.py

# Test with verbose output
python -m pytest test_agent_system.py -v
```

## 📁 Project Structure

```
ai_agents/
├── agent_system.py          # Main PRP agent system
├── demo.py                  # Interactive demo script
├── test_agent_system.py     # Comprehensive test suite
├── config.py                # Configuration management
├── react_agent.py           # React agent implementation
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── AGENT_SYSTEM_README.md   # PRP system documentation
└── README.md                # This file
```

## 🎯 Use Cases

**React Agent:**
- Web search and information retrieval
- Conversational AI assistance
- Real-time data queries

**PRP Agent System:**
- Automated task execution
- Safe code execution in sandboxes
- Multi-step workflow automation
- System administration tasks
- Development environment setup
- Data processing pipelines

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

MIT 