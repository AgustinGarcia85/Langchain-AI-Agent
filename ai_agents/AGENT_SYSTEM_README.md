# PRP: LangChain + Daytona Agent System

A modular AI agent system that provides safe, coordinated execution of tasks using isolated sandboxes with shared memory and intelligent orchestration.

## 🏗️ Architecture

The system consists of four specialized agents working together:

- **🤖 Planner Agent**: Breaks down complex tasks into executable steps
- **⚡ Executor Agent**: Safely executes commands in Daytona sandbox
- **🔍 Reviewer Agent**: Validates and reviews execution outputs
- **🎯 Orchestrator**: Coordinates all agents and compiles final responses

## ✨ Features

- **Safe Execution**: All code runs in isolated Daytona sandboxes
- **Shared Memory**: Agents maintain conversation history across interactions
- **Intelligent Planning**: AI-powered task breakdown and optimization
- **Quality Assurance**: Automated review and validation of all outputs
- **Secure Credentials**: Environment-based API key management
- **Modular Design**: Easy to extend and customize individual agents

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Setup

Copy the example environment file and add your API keys:

```bash
cp .env.example .env
```

Edit `.env` with your actual API keys:

```bash
# OpenAI API Configuration
OPENAI_API_KEY=sk-your-actual-openai-key

# Daytona Configuration  
DAYTONA_API_KEY=your-actual-daytona-key
DAYTONA_SERVER_URL=https://api.daytona.io
```

### 3. Run the System

```bash
python agent_system.py
```

## 📖 Usage Examples

### Basic Task Execution

```python
from agent_system import Orchestrator

orchestrator = Orchestrator()
result = orchestrator.run("Fetch the current date and list files")
print(result)
```

### Individual Agent Usage

```python
from agent_system import PlannerAgent, ExecutorAgent, ReviewerAgent

# Plan a task
planner = PlannerAgent()
steps = planner.run("Install and configure a web server")

# Execute a command
executor = ExecutorAgent()
result = executor.run("date")

# Review an output
reviewer = ReviewerAgent()
review = reviewer.run(result, "date command")
```

### Custom Tasks

The system can handle various types of tasks:

- **System Operations**: File management, process monitoring
- **Development Tasks**: Code compilation, testing, deployment
- **Data Processing**: File analysis, data transformation
- **Network Operations**: API calls, connectivity testing

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key for LLM operations | Yes |
| `DAYTONA_API_KEY` | Daytona API key for sandbox execution | Yes |
| `DAYTONA_SERVER_URL` | Daytona server endpoint | Yes |

### Model Configuration

You can customize the OpenAI model and parameters in `agent_system.py`:

```python
llm = ChatOpenAI(
    temperature=0,  # Adjust creativity (0 = deterministic, 1 = creative)
    openai_api_key=OPENAI_API_KEY,
    model="gpt-4"  # Use different models as needed
)
```

## 🧪 Testing

### Unit Tests

Run the included test suite:

```bash
python -m pytest test_agent_system.py -v
```

### Manual Testing

Test with simple commands first:

```bash
python agent_system.py
```

This will run the example task: "Fetch the current date and list files"

## 🔒 Security Features

- **Sandboxed Execution**: All commands run in isolated Daytona environments
- **No Hardcoded Credentials**: All API keys loaded from environment variables
- **Input Validation**: Commands are cleaned and validated before execution
- **Error Handling**: Comprehensive error handling prevents system compromise

## 🚨 Error Handling

The system includes robust error handling:

- **API Failures**: Graceful degradation when external services are unavailable
- **Invalid Commands**: Safe execution with proper error reporting
- **Memory Issues**: Fallback mechanisms for memory operations
- **Network Problems**: Retry logic for transient failures

## 📊 Memory Management

All agents share a `ConversationBufferMemory` instance that:

- Stores input/output pairs for each agent interaction
- Maintains conversation context across the entire workflow
- Enables agents to reference previous decisions and results
- Provides audit trail for debugging and analysis

## 🔄 Workflow Process

1. **Task Input**: User provides a high-level task description
2. **Planning**: Planner Agent breaks down the task into executable steps
3. **Execution**: Executor Agent runs each step in Daytona sandbox
4. **Review**: Reviewer Agent validates each step's output
5. **Orchestration**: Final compilation and response generation
6. **Memory Storage**: All interactions saved to shared memory

## 🛠️ Troubleshooting

### Common Issues

**Daytona Connection Failed**
- Verify your Daytona API key and server URL
- Check network connectivity to Daytona servers
- Ensure your Daytona account has sufficient credits

**OpenAI API Errors**
- Verify your OpenAI API key is valid
- Check your OpenAI account has sufficient credits
- Ensure the API key has the correct permissions

**Memory Issues**
- Check available system memory
- Verify write permissions in the working directory

### Debug Mode

Enable verbose logging by modifying the agent classes to include debug prints.

## 🔮 Future Enhancements

- **Multi-Agent Parallelization**: Execute multiple steps simultaneously
- **Advanced Memory Types**: Implement more sophisticated memory systems
- **Custom Agent Types**: Allow users to define specialized agents
- **Web Interface**: Add Streamlit-based UI for easier interaction
- **API Endpoints**: REST API for integration with other systems
- **Plugin System**: Extensible architecture for custom functionality

## 📚 API Reference

### PlannerAgent

```python
class PlannerAgent:
    def run(self, task: str) -> str:
        """Break down a task into executable steps"""
```

### ExecutorAgent

```python
class ExecutorAgent:
    def run(self, command: str) -> Any:
        """Execute a command in Daytona sandbox"""
```

### ReviewerAgent

```python
class ReviewerAgent:
    def run(self, output: Any, original_command: str = None) -> str:
        """Review and validate execution output"""
```

### Orchestrator

```python
class Orchestrator:
    def run(self, task: str) -> str:
        """Execute complete workflow for a task"""
    
    def get_memory(self) -> List[Any]:
        """Get conversation memory"""
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **LangChain**: For the excellent agent framework
- **Daytona**: For secure sandboxed execution
- **OpenAI**: For powerful language models
- **Open Source Community**: For inspiration and support

---

**Note**: This system is designed for development and testing environments. Use in production with appropriate security reviews and monitoring.