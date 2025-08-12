import unittest
from unittest.mock import Mock, patch, MagicMock
import os
import sys
from dotenv import load_dotenv

# Load environment variables for testing
load_dotenv()

# Mock Daytona imports for testing
sys.modules['daytona'] = Mock()
sys.modules['daytona.Daytona'] = Mock()
sys.modules['daytona.DaytonaConfig'] = Mock()

# Import the agent system
from agent_system import (
    PlannerAgent, 
    ExecutorAgent, 
    ReviewerAgent, 
    Orchestrator,
    memory
)

class TestPlannerAgent(unittest.TestCase):
    """Test cases for PlannerAgent"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.planner = PlannerAgent()
        self.test_task = "Install and configure a web server"
    
    @patch('agent_system.llm')
    def test_plan_task_success(self, mock_llm):
        """Test successful task planning"""
        # Mock LLM response
        mock_response = Mock()
        mock_response.content = "1. - Check system requirements\n2. - Install web server\n3. - Configure server"
        mock_llm.invoke.return_value = mock_response
        
        result = self.planner.run(self.test_task)
        
        # Verify result
        self.assertIn("1. - Check system requirements", result)
        self.assertIn("2. - Install web server", result)
        self.assertIn("3. - Configure server", result)
        
        # Verify LLM was called
        mock_llm.invoke.assert_called_once()
    
    @patch('agent_system.llm')
    def test_plan_task_error(self, mock_llm):
        """Test task planning with error"""
        # Mock LLM error
        mock_llm.invoke.side_effect = Exception("API Error")
        
        result = self.planner.run(self.test_task)
        
        # Verify error handling
        self.assertIn("Planner error", result)
        self.assertIn("API Error", result)

class TestExecutorAgent(unittest.TestCase):
    """Test cases for ExecutorAgent"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.executor = ExecutorAgent()
        self.test_command = "date"
    
    @patch('agent_system.daytona')
    def test_execute_command_success(self, mock_daytona):
        """Test successful command execution"""
        # Mock Daytona response
        mock_daytona.execute.return_value = "Mon Dec 25 10:30:00 UTC 2023"
        
        result = self.executor.run(self.test_command)
        
        # Verify result
        self.assertEqual(result, "Mon Dec 25 10:30:00 UTC 2023")
        
        # Verify Daytona was called
        mock_daytona.execute.assert_called_once_with(self.test_command)
    
    def test_execute_command_no_daytona(self):
        """Test command execution when Daytona is not available"""
        # Temporarily set daytona to None
        original_daytona = self.executor.daytona
        self.executor.daytona = None
        
        result = self.executor.run(self.test_command)
        
        # Verify error handling
        self.assertIn("Daytona not available", result)
        
        # Restore daytona
        self.executor.daytona = original_daytona
    
    @patch('agent_system.daytona')
    def test_execute_command_error(self, mock_daytona):
        """Test command execution with error"""
        # Mock Daytona error
        mock_daytona.execute.side_effect = Exception("Execution failed")
        
        result = self.executor.run(self.test_command)
        
        # Verify error handling
        self.assertIn("Execution error", result)
        self.assertIn("Execution failed", result)
    
    def test_clean_command_formatting(self):
        """Test command cleaning and formatting"""
        test_cases = [
            ("1. - date", "date"),
            ("2. - ls -la", "ls -la"),
            ("3. - echo hello", "echo hello"),
            ("- pwd", "pwd"),
            ("   date   ", "date"),
        ]
        
        for input_cmd, expected in test_cases:
            with self.subTest(input_cmd=input_cmd):
                # Mock Daytona to return success
                with patch.object(self.executor, 'daytona') as mock_daytona:
                    mock_daytona.execute.return_value = "success"
                    self.executor.run(input_cmd)
                    # Verify the cleaned command was passed to Daytona
                    mock_daytona.execute.assert_called_with(expected)

class TestReviewerAgent(unittest.TestCase):
    """Test cases for ReviewerAgent"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.reviewer = ReviewerAgent()
        self.test_output = "Mon Dec 25 10:30:00 UTC 2023"
        self.test_command = "date"
    
    @patch('agent_system.llm')
    def test_review_output_success(self, mock_llm):
        """Test successful output review"""
        # Mock LLM response
        mock_response = Mock()
        mock_response.content = "Output is valid and complete. Shows current date and time."
        mock_llm.invoke.return_value = mock_response
        
        result = self.reviewer.run(self.test_output, self.test_command)
        
        # Verify result
        self.assertIn("Output is valid and complete", result)
        
        # Verify LLM was called
        mock_llm.invoke.assert_called_once()
    
    @patch('agent_system.llm')
    def test_review_output_error(self, mock_llm):
        """Test output review with error"""
        # Mock LLM error
        mock_llm.invoke.side_effect = Exception("Review failed")
        
        result = self.reviewer.run(self.test_output, self.test_command)
        
        # Verify error handling
        self.assertIn("Review error", result)
        self.assertIn("Review failed", result)
    
    def test_review_output_no_command(self):
        """Test output review without original command"""
        with patch.object(self.reviewer, 'llm') as mock_llm:
            mock_response = Mock()
            mock_response.content = "Review completed"
            mock_llm.invoke.return_value = mock_response
            
            result = self.reviewer.run(self.test_output)
            
            # Verify it works without original command
            self.assertEqual(result, "Review completed")

class TestOrchestrator(unittest.TestCase):
    """Test cases for Orchestrator"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.orchestrator = Orchestrator()
        self.test_task = "Fetch current date and list files"
    
    @patch.object(PlannerAgent, 'run')
    @patch.object(ExecutorAgent, 'run')
    @patch.object(ReviewerAgent, 'run')
    @patch.object(Orchestrator, '_compile_final_response')
    def test_orchestrate_workflow_success(self, mock_compile, mock_review, mock_execute, mock_plan):
        """Test successful workflow orchestration"""
        # Mock all agent responses
        mock_plan.return_value = "1. - date\n2. - ls -la"
        mock_execute.side_effect = ["Mon Dec 25 10:30:00 UTC 2023", "file1.txt file2.txt"]
        mock_review.side_effect = ["Date output is valid", "File listing is complete"]
        mock_compile.return_value = "Task completed successfully"
        
        result = self.orchestrator.run(self.test_task)
        
        # Verify final result
        self.assertEqual(result, "Task completed successfully")
        
        # Verify all agents were called
        mock_plan.assert_called_once_with(self.test_task)
        self.assertEqual(mock_execute.call_count, 2)
        self.assertEqual(mock_review.call_count, 2)
        mock_compile.assert_called_once()
    
    @patch.object(PlannerAgent, 'run')
    def test_orchestrate_workflow_planning_error(self, mock_plan):
        """Test workflow orchestration with planning error"""
        # Mock planning error
        mock_plan.return_value = "Planner error: API failed"
        
        result = self.orchestrator.run(self.test_task)
        
        # Verify error handling
        self.assertIn("Planner error", result)
    
    def test_compile_final_response(self):
        """Test final response compilation"""
        task = "Test task"
        step_results = [
            {"step": "step1", "result": "result1"},
            {"step": "step2", "result": "result2"}
        ]
        
        with patch.object(self.orchestrator, 'llm') as mock_llm:
            mock_response = Mock()
            mock_response.content = "Compiled response"
            mock_llm.invoke.return_value = mock_response
            
            result = self.orchestrator._compile_final_response(task, step_results)
            
            # Verify result
            self.assertEqual(result, "Compiled response")
    
    def test_get_memory(self):
        """Test memory retrieval"""
        # Add some test data to memory
        memory.save_context(
            {"input": "test input"},
            {"output": "test output"}
        )
        
        memory_content = self.orchestrator.get_memory()
        
        # Verify memory is accessible
        self.assertIsInstance(memory_content, list)
        self.assertGreater(len(memory_content), 0)

class TestMemoryIntegration(unittest.TestCase):
    """Test cases for memory integration across agents"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Clear memory before each test
        memory.clear()
        self.planner = PlannerAgent()
        self.executor = ExecutorAgent()
        self.reviewer = ReviewerAgent()
    
    def test_memory_persistence_across_agents(self):
        """Test that memory persists across different agents"""
        # Use planner
        with patch.object(self.planner, 'llm') as mock_llm:
            mock_response = Mock()
            mock_response.content = "1. - test"
            mock_llm.invoke.return_value = mock_response
            self.planner.run("test task")
        
        # Use executor
        with patch.object(self.executor, 'daytona') as mock_daytona:
            mock_daytona.execute.return_value = "test result"
            self.executor.run("test command")
        
        # Use reviewer
        with patch.object(self.reviewer, 'llm') as mock_llm:
            mock_response = Mock()
            mock_response.content = "test review"
            mock_llm.invoke.return_value = mock_response
            self.reviewer.run("test output")
        
        # Check memory content
        memory_content = memory.load_memory_variables({})["history"]
        
        # Verify all interactions are stored
        self.assertEqual(len(memory_content), 3)
        
        # Verify content types
        self.assertTrue(any("Planner generated steps" in str(msg) for msg in memory_content))
        self.assertTrue(any("Execution result" in str(msg) for msg in memory_content))
        self.assertTrue(any("Review:" in str(msg) for msg in memory_content))

class TestErrorHandling(unittest.TestCase):
    """Test cases for error handling and edge cases"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.orchestrator = Orchestrator()
    
    def test_empty_task_handling(self):
        """Test handling of empty tasks"""
        with patch.object(PlannerAgent, 'run') as mock_plan:
            mock_plan.return_value = ""
            
            result = self.orchestrator.run("")
            
            # Verify graceful handling
            self.assertIsInstance(result, str)
    
    def test_malformed_steps_handling(self):
        """Test handling of malformed step outputs"""
        with patch.object(PlannerAgent, 'run') as mock_plan:
            mock_plan.return_value = "Invalid step format\n\n\n"
            
            with patch.object(ExecutorAgent, 'run') as mock_execute:
                mock_execute.return_value = "No command to execute"
                
                result = self.orchestrator.run("test task")
                
                # Verify graceful handling
                self.assertIsInstance(result, str)

def run_tests():
    """Run all tests with verbose output"""
    # Create test suite
    test_suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    # Check if required environment variables are set
    required_vars = ['OPENAI_API_KEY', 'DAYTONA_API_KEY', 'DAYTONA_SERVER_URL']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"⚠️  Warning: Missing environment variables: {', '.join(missing_vars)}")
        print("Some tests may fail. Set up your .env file for full testing.")
        print()
    
    # Run tests
    success = run_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)