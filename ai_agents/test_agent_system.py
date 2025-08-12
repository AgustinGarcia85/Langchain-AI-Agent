"""
Unit tests for the Multi-Agent System

Tests all components: PlannerAgent, ExecutorAgent, ReviewerAgent, 
Orchestrator, and DaytonaExecutor
"""

import pytest
import os
import json
from unittest.mock import Mock, patch, MagicMock
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain.schema import AIMessage

from agent_system import (
    AgentConfig,
    DaytonaExecutor,
    PlannerAgent,
    ExecutorAgent,
    ReviewerAgent,
    Orchestrator,
    create_agent_system
)

class TestDaytonaExecutor:
    """Test the DaytonaExecutor class"""
    
    def test_init(self):
        """Test DaytonaExecutor initialization"""
        executor = DaytonaExecutor(api_key="test_key", server_url="test_url")
        assert executor.api_key == "test_key"
        assert executor.server_url == "test_url"
    
    def test_execute_date_command(self):
        """Test executing a date command"""
        executor = DaytonaExecutor()
        result = executor.execute_command("date")
        
        assert result["exit_code"] == 0
        assert "UTC 2024" in result["stdout"]
        assert result["stderr"] == ""
        assert result["execution_time"] > 0
    
    def test_execute_ls_command(self):
        """Test executing a list command"""
        executor = DaytonaExecutor()
        result = executor.execute_command("ls -la")
        
        assert result["exit_code"] == 0
        assert "file1.txt" in result["stdout"]
        assert result["stderr"] == ""
    
    def test_execute_python_command(self):
        """Test executing a Python command"""
        executor = DaytonaExecutor()
        result = executor.execute_command("python script.py")
        
        assert result["exit_code"] == 0
        assert "Script executed successfully" in result["stdout"]
        assert "Result: 42" in result["stdout"]
    
    def test_execute_generic_command(self):
        """Test executing a generic command"""
        executor = DaytonaExecutor()
        result = executor.execute_command("echo hello")
        
        assert result["exit_code"] == 0
        assert "echo hello" in result["stdout"]

class TestPlannerAgent:
    """Test the PlannerAgent class"""
    
    @pytest.fixture
    def mock_llm(self):
        """Create a mock LLM"""
        llm = Mock(spec=ChatOpenAI)
        response = Mock()
        response.content = """1. Get current date
2. List files in directory
3. Validate results"""
        llm.invoke.return_value = response
        return llm
    
    @pytest.fixture
    def memory(self):
        """Create shared memory"""
        return ConversationBufferMemory(memory_key="history", return_messages=True)
    
    def test_init(self, mock_llm, memory):
        """Test PlannerAgent initialization"""
        planner = PlannerAgent(mock_llm, memory)
        assert planner.llm == mock_llm
        assert planner.memory == memory
        assert "task planning agent" in planner.system_prompt.lower()
    
    def test_run_success(self, mock_llm, memory):
        """Test successful task planning"""
        planner = PlannerAgent(mock_llm, memory)
        steps = planner.run("Test task")
        
        assert len(steps) == 3
        assert "Get current date" in steps[0]
        assert "List files in directory" in steps[1]
        assert "Validate results" in steps[2]
        
        # Verify LLM was called
        mock_llm.invoke.assert_called_once()
        
        # Verify memory was updated
        memory_vars = memory.load_memory_variables({})
        assert len(memory_vars["history"]) > 0
    
    def test_run_with_llm_error(self, memory):
        """Test handling LLM errors"""
        mock_llm = Mock(spec=ChatOpenAI)
        mock_llm.invoke.side_effect = Exception("API Error")
        
        planner = PlannerAgent(mock_llm, memory)
        steps = planner.run("Test task")
        
        assert len(steps) == 1
        assert "Error in planning" in steps[0]

class TestExecutorAgent:
    """Test the ExecutorAgent class"""
    
    @pytest.fixture
    def mock_daytona(self):
        """Create a mock Daytona executor"""
        daytona = Mock(spec=DaytonaExecutor)
        daytona.execute_command.return_value = {
            "stdout": "Command output",
            "stderr": "",
            "exit_code": 0,
            "execution_time": 0.5
        }
        return daytona
    
    @pytest.fixture
    def memory(self):
        """Create shared memory"""
        return ConversationBufferMemory(memory_key="history", return_messages=True)
    
    def test_init(self, mock_daytona, memory):
        """Test ExecutorAgent initialization"""
        executor = ExecutorAgent(mock_daytona, memory)
        assert executor.daytona == mock_daytona
        assert executor.memory == memory
    
    def test_run_success(self, mock_daytona, memory):
        """Test successful command execution"""
        executor = ExecutorAgent(mock_daytona, memory)
        result = executor.run("test command")
        
        assert result["exit_code"] == 0
        assert result["stdout"] == "Command output"
        
        # Verify Daytona was called
        mock_daytona.execute_command.assert_called_once_with("test command")
        
        # Verify memory was updated
        memory_vars = memory.load_memory_variables({})
        assert len(memory_vars["history"]) > 0
    
    def test_run_with_error(self, memory):
        """Test handling execution errors"""
        mock_daytona = Mock(spec=DaytonaExecutor)
        mock_daytona.execute_command.side_effect = Exception("Execution failed")
        
        executor = ExecutorAgent(mock_daytona, memory)
        result = executor.run("test command")
        
        assert result["exit_code"] == 1
        assert "Execution failed" in result["stderr"]
        assert "error" in result

class TestReviewerAgent:
    """Test the ReviewerAgent class"""
    
    @pytest.fixture
    def mock_llm(self):
        """Create a mock LLM"""
        llm = Mock(spec=ChatOpenAI)
        response = Mock()
        response.content = """STATUS: SUCCESS
FEEDBACK: Command executed successfully with expected output
SUGGESTIONS: No improvements needed"""
        llm.invoke.return_value = response
        return llm
    
    @pytest.fixture
    def memory(self):
        """Create shared memory"""
        return ConversationBufferMemory(memory_key="history", return_messages=True)
    
    def test_init(self, mock_llm, memory):
        """Test ReviewerAgent initialization"""
        reviewer = ReviewerAgent(mock_llm, memory)
        assert reviewer.llm == mock_llm
        assert reviewer.memory == memory
        assert "code execution reviewer" in reviewer.system_prompt.lower()
    
    def test_run_success(self, mock_llm, memory):
        """Test successful result review"""
        reviewer = ReviewerAgent(mock_llm, memory)
        
        execution_result = {
            "stdout": "Test output",
            "stderr": "",
            "exit_code": 0,
            "execution_time": 0.1
        }
        
        review = reviewer.run("test command", execution_result)
        
        assert review["status"] == "SUCCESS"
        assert "successfully" in review["feedback"].lower()
        
        # Verify LLM was called
        mock_llm.invoke.assert_called_once()
        
        # Verify memory was updated
        memory_vars = memory.load_memory_variables({})
        assert len(memory_vars["history"]) > 0
    
    def test_run_with_llm_error(self, memory):
        """Test handling LLM errors during review"""
        mock_llm = Mock(spec=ChatOpenAI)
        mock_llm.invoke.side_effect = Exception("Review failed")
        
        reviewer = ReviewerAgent(mock_llm, memory)
        execution_result = {"stdout": "test", "stderr": "", "exit_code": 0}
        
        review = reviewer.run("test command", execution_result)
        
        assert review["status"] == "ERROR"
        assert "Review failed" in review["feedback"]

class TestOrchestrator:
    """Test the Orchestrator class"""
    
    @pytest.fixture
    def config(self):
        """Create test configuration"""
        return AgentConfig(
            openai_api_key="test_key",
            daytona_api_key="daytona_key",
            daytona_server_url="http://test.com"
        )
    
    @patch('agent_system.ChatOpenAI')
    @patch('agent_system.DaytonaExecutor')
    def test_init(self, mock_daytona_class, mock_llm_class, config):
        """Test Orchestrator initialization"""
        orchestrator = Orchestrator(config)
        
        assert orchestrator.config == config
        assert orchestrator.memory is not None
        assert orchestrator.planner is not None
        assert orchestrator.executor is not None
        assert orchestrator.reviewer is not None
        
        # Verify components were initialized
        mock_llm_class.assert_called_once()
        mock_daytona_class.assert_called_once()
    
    @patch('agent_system.ChatOpenAI')
    @patch('agent_system.DaytonaExecutor')
    def test_run_success(self, mock_daytona_class, mock_llm_class, config):
        """Test successful task orchestration"""
        # Mock the LLM responses
        mock_llm = Mock()
        mock_llm_class.return_value = mock_llm
        
        # Mock planner response
        planner_response = Mock()
        planner_response.content = "1. Get date\n2. List files"
        
        # Mock reviewer response
        reviewer_response = Mock()
        reviewer_response.content = "STATUS: SUCCESS\nFEEDBACK: Good\nSUGGESTIONS: None"
        
        mock_llm.invoke.side_effect = [planner_response, reviewer_response, reviewer_response]
        
        # Mock Daytona executor
        mock_daytona = Mock()
        mock_daytona.execute_command.return_value = {
            "stdout": "Test output",
            "stderr": "",
            "exit_code": 0,
            "execution_time": 0.1
        }
        mock_daytona_class.return_value = mock_daytona
        
        orchestrator = Orchestrator(config)
        result = orchestrator.run("Test task")
        
        assert result["status"] == "SUCCESS"
        assert "Test task" in result["original_task"]
        assert len(result["steps"]) == 2
        assert len(result["results"]) == 2
        assert "summary" in result
    
    @patch('agent_system.ChatOpenAI')
    @patch('agent_system.DaytonaExecutor')
    def test_run_with_planning_error(self, mock_daytona_class, mock_llm_class, config):
        """Test orchestration with planning error"""
        mock_llm = Mock()
        mock_llm_class.return_value = mock_llm
        mock_llm.invoke.side_effect = Exception("Planning failed")
        
        orchestrator = Orchestrator(config)
        result = orchestrator.run("Test task")
        
        assert result["status"] == "ERROR"
        assert "Failed to create execution plan" in result["message"]
    
    def test_get_memory_summary(self, config):
        """Test memory summary generation"""
        with patch('agent_system.ChatOpenAI'), patch('agent_system.DaytonaExecutor'):
            orchestrator = Orchestrator(config)
            
            # Add some content to memory
            orchestrator.memory.save_context(
                {"input": "test input"}, 
                {"output": "test output"}
            )
            
            summary = orchestrator._get_memory_summary()
            
            assert "message_count" in summary
            assert summary["message_count"] > 0
            assert "recent_messages" in summary
    
    def test_generate_summary(self, config):
        """Test task execution summary generation"""
        with patch('agent_system.ChatOpenAI'), patch('agent_system.DaytonaExecutor'):
            orchestrator = Orchestrator(config)
            
            results = [
                {
                    "step_number": 1,
                    "step_description": "Test step",
                    "review": {"status": "SUCCESS"}
                }
            ]
            
            summary = orchestrator._generate_summary("Test task", results)
            
            assert "Test task" in summary
            assert "1/1 steps successfully" in summary
            assert "✅" in summary

class TestCreateAgentSystem:
    """Test the create_agent_system factory function"""
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'})
    def test_create_with_env_vars(self):
        """Test creating agent system with environment variables"""
        with patch('agent_system.Orchestrator') as mock_orchestrator:
            create_agent_system()
            
            # Verify Orchestrator was called with correct config
            mock_orchestrator.assert_called_once()
            config = mock_orchestrator.call_args[0][0]
            assert config.openai_api_key == 'test_key'
    
    def test_create_without_api_key(self):
        """Test creating agent system without required API key"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="OPENAI_API_KEY is required"):
                create_agent_system()

class TestAgentConfig:
    """Test the AgentConfig dataclass"""
    
    def test_init_required_only(self):
        """Test initialization with required fields only"""
        config = AgentConfig(openai_api_key="test_key")
        
        assert config.openai_api_key == "test_key"
        assert config.daytona_api_key is None
        assert config.daytona_server_url is None
        assert config.temperature == 0.1
        assert config.model_name == "gpt-3.5-turbo"
        assert config.max_tokens == 1000
    
    def test_init_all_fields(self):
        """Test initialization with all fields"""
        config = AgentConfig(
            openai_api_key="openai_key",
            daytona_api_key="daytona_key",
            daytona_server_url="http://test.com",
            temperature=0.5,
            model_name="gpt-4",
            max_tokens=2000
        )
        
        assert config.openai_api_key == "openai_key"
        assert config.daytona_api_key == "daytona_key"
        assert config.daytona_server_url == "http://test.com"
        assert config.temperature == 0.5
        assert config.model_name == "gpt-4"
        assert config.max_tokens == 2000

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment variables"""
    test_env = {
        'OPENAI_API_KEY': 'test_openai_key',
        'DAYTONA_API_KEY': 'test_daytona_key',
        'DAYTONA_SERVER_URL': 'http://test-daytona.com'
    }
    
    # Store original values
    original_values = {}
    for key, value in test_env.items():
        original_values[key] = os.environ.get(key)
        os.environ[key] = value
    
    yield
    
    # Restore original values
    for key, value in original_values.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value

if __name__ == "__main__":
    pytest.main([__file__, "-v"])