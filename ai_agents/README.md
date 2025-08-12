# AI Agents Collection

This project contains multiple AI agent implementations using LangChain, including a React agent with web search capabilities and a comprehensive multi-agent system with Daytona integration.

## 🤖 Agents Available

### 1. React Agent (LangChain + LangSmith)
A web-search-enabled AI assistant using the LangChain ReAct agent framework with Streamlit UI.

### 2. Multi-Agent System (LangChain + Daytona)
A sophisticated multi-agent system with coordinated task planning, execution, and review capabilities.

---

## 🚀 Multi-Agent System

### Overview
The multi-agent system implements a coordinated AI workflow where:
- **Planner Agent**: Breaks down user tasks into executable steps
- **Executor Agent**: Runs code/commands within a Daytona sandbox
- **Reviewer Agent**: Validates results and flags errors  
- **Orchestrator**: Coordinates all agents with shared memory

### Key Features
- ✅ Safe execution using isolated Daytona sandboxes
- ✅ Coordinated multi-step workflows with persistent memory
- ✅ Secure credential handling via environment variables
- ✅ Comprehensive error handling and recovery
- ✅ Detailed logging and result tracking
- ✅ Modular, extensible architecture

### Architecture

```
User Task → Orchestrator → Planner Agent → Steps
                ↓
         Executor Agent ← → Daytona Sandbox
                ↓
         Reviewer Agent → Validation & Feedback
                ↓
         Final Response ← Orchestrator
```

### Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables** - Copy `.env.sample` to `.env` and fill in your API keys:
   ```bash
   cp .env.sample .env
   # Edit .env with your actual API keys
   ```

3. **Run the basic test**:
   ```bash
   python agent_system.py
   ```

4. **Try the examples**:
   ```bash
   python example_usage.py
   ```

### Environment Variables

Create a `.env` file with the following variables:

```env
# Required
OPENAI_API_KEY=your-openai-api-key

# Daytona Configuration (optional for mock mode)
DAYTONA_API_KEY=your-daytona-api-key
DAYTONA_SERVER_URL=https://your-daytona-server.com

# Optional Configuration
AGENT_TEMPERATURE=0.1
OPENAI_MODEL=gpt-3.5-turbo
MAX_TOKENS=1000

# LangSmith (optional for tracing)
LANGSMITH_API_KEY=your-langsmith-key
LANGSMITH_TRACING=true
```

### Usage Examples

#### Basic Usage
```python
from agent_system import create_agent_system

# Create the orchestrator
orchestrator = create_agent_system()

# Run a task
result = orchestrator.run("Get current date and list files")

# Check results
print(f"Status: {result['status']}")
print(f"Summary: {result['summary']}")
```

#### Advanced Usage
```python
from agent_system import Orchestrator, AgentConfig

# Custom configuration
config = AgentConfig(
    openai_api_key="your-key",
    temperature=0.2,
    model_name="gpt-4",
    max_tokens=2000
)

# Create orchestrator with custom config
orchestrator = Orchestrator(config)

# Complex task
task = """Create a Python data analysis script that:
1. Generates sample data
2. Performs statistical analysis
3. Creates visualizations
4. Saves results to files"""

result = orchestrator.run(task)
```

### Running Tests

```bash
# Run all tests
python -m pytest test_agent_system.py -v

# Run specific test class
python -m pytest test_agent_system.py::TestOrchestrator -v

# Run with coverage
python -m pytest test_agent_system.py --cov=agent_system
```

### Example Scripts

The `example_usage.py` script provides several demonstrations:

1. **Basic Operations**: File operations and system commands
2. **Python Analysis**: Data analysis and script generation
3. **Web Development**: HTML/CSS creation
4. **System Information**: Gathering system details
5. **Error Handling**: Demonstrating error recovery
6. **Memory Demo**: Showing persistent memory across tasks
7. **Interactive Mode**: Real-time task processing

```bash
python example_usage.py
```

### API Reference

#### Orchestrator Class

```python
class Orchestrator:
    def __init__(self, config: AgentConfig)
    def run(self, task: str) -> Dict[str, Any]
```

**Returns:**
```python
{
    "status": "SUCCESS" | "ERROR",
    "message": "Description of execution",
    "original_task": "Original user task",
    "steps": ["List of planned steps"],
    "results": [
        {
            "step_number": 1,
            "step_description": "Step description",
            "execution_result": {...},
            "review": {...}
        }
    ],
    "memory": {...},
    "summary": "Human-readable summary"
}
```

#### Individual Agents

```python
# Planner Agent
planner = PlannerAgent(llm, memory)
steps = planner.run("Task description")

# Executor Agent  
executor = ExecutorAgent(daytona_executor, memory)
result = executor.run("Command to execute")

# Reviewer Agent
reviewer = ReviewerAgent(llm, memory)
review = reviewer.run("Command", execution_result)
```

---

## 🔍 React Agent (Original)

### Features
- Web search via Brave Search API
- Conversational interface powered by Streamlit
- LangSmith tracing for agent runs
- Secure environment variable management

### Setup for React Agent
1. **Install dependencies** (already done above)
2. **Configure `.env`** with Brave Search API key
3. **Run the Streamlit app**:
   ```bash
   streamlit run react_agent.py
   ```

### Usage
- Enter your query in the text box and click "Send"
- The agent will use web search for real-time information queries
- All agent runs are tracked with LangSmith for observability

---

## 🛠 Development

### Project Structure
```
ai_agents/
├── agent_system.py          # Multi-agent system implementation
├── react_agent.py           # Original React agent
├── test_agent_system.py     # Comprehensive tests
├── example_usage.py         # Usage examples and demos
├── requirements.txt         # Python dependencies
├── .env.sample             # Environment variable template
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

### Adding New Agents

To extend the system with new agents:

1. **Create agent class**:
```python
class MyCustomAgent:
    def __init__(self, llm, memory):
        self.llm = llm
        self.memory = memory
    
    def run(self, input_data):
        # Your agent logic here
        result = self.llm.invoke(...)
        self.memory.save_context(...)
        return result
```

2. **Integrate with orchestrator**:
```python
# In Orchestrator.__init__()
self.my_agent = MyCustomAgent(self.llm, self.memory)

# In Orchestrator.run()
custom_result = self.my_agent.run(data)
```

3. **Add tests**:
```python
class TestMyCustomAgent:
    def test_run_success(self):
        # Test your agent
        pass
```

### Daytona Integration

The current implementation includes a mock Daytona executor for demonstration. To integrate with real Daytona:

1. **Install Daytona SDK** (already in requirements.txt)
2. **Replace mock implementation**:
```python
from daytona import Daytona, DaytonaConfig

class DaytonaExecutor:
    def __init__(self, api_key, server_url):
        config = DaytonaConfig(api_key=api_key, server_url=server_url)
        self.daytona = Daytona(config=config)
    
    def execute_command(self, command):
        return self.daytona.execute(command)
```

### Memory Management

The system uses LangChain's `ConversationBufferMemory` for shared state:

```python
memory = ConversationBufferMemory(
    memory_key="history",
    return_messages=True,
    human_prefix="User",
    ai_prefix="Assistant"
)
```

Memory is automatically managed and shared across all agents in the orchestrator.

## 🔒 Security

- **Never commit your `.env` file** - it's excluded via `.gitignore`
- API keys are loaded securely from environment variables
- Daytona sandboxes provide isolated execution environments
- All inputs are validated before processing

## 📊 Monitoring & Observability

- Comprehensive logging throughout the system
- LangSmith integration for tracing (optional)
- Detailed execution results and reviews
- Memory usage tracking

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Troubleshooting

### Common Issues

1. **"OPENAI_API_KEY is required" error**
   - Ensure `.env` file exists with valid API key
   - Check that `python-dotenv` is installed

2. **Import errors**
   - Run `pip install -r requirements.txt`
   - Ensure you're in the correct directory

3. **Agent execution failures**
   - Check API key validity and quotas
   - Review logs for detailed error messages
   - Ensure network connectivity

4. **Memory issues**
   - Large conversations may hit token limits
   - Consider implementing memory truncation for long sessions

### Getting Help

- Check the example scripts for usage patterns
- Review test files for expected behaviors
- Enable debug logging for detailed troubleshooting
- Open an issue for bugs or feature requests

---

**Happy Agent Building! 🤖✨** 