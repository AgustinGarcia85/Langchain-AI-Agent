"""
Multi-Agent System with LangChain and Daytona Integration

This module implements a coordinated AI agent system where:
- Planner Agent: Breaks down user tasks into executable steps
- Executor Agent: Runs code/commands within a Daytona sandbox
- Reviewer Agent: Validates results and flags errors
- Orchestrator: Coordinates all agents with shared memory

All agents share memory and API keys are loaded securely via .env
"""

import os
import logging
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

@dataclass
class AgentConfig:
    """Configuration for the agent system"""
    openai_api_key: str
    daytona_api_key: Optional[str] = None
    daytona_server_url: Optional[str] = None
    temperature: float = 0.1
    model_name: str = "gpt-3.5-turbo"
    max_tokens: int = 1000

class DaytonaExecutor:
    """Mock Daytona executor for demonstration (replace with actual Daytona SDK)"""
    
    def __init__(self, api_key: Optional[str] = None, server_url: Optional[str] = None):
        self.api_key = api_key
        self.server_url = server_url
        logger.info("DaytonaExecutor initialized")
    
    def execute_command(self, command: str) -> Dict[str, Any]:
        """
        Execute a command in a Daytona sandbox
        This is a mock implementation - replace with actual Daytona SDK calls
        """
        logger.info(f"Executing command: {command}")
        
        # Mock execution results based on command type
        if "date" in command.lower():
            return {
                "stdout": "Mon Dec 16 10:30:45 UTC 2024",
                "stderr": "",
                "exit_code": 0,
                "execution_time": 0.1
            }
        elif "ls" in command.lower() or "list" in command.lower():
            return {
                "stdout": "file1.txt\nfile2.py\ndata.json\nREADME.md",
                "stderr": "",
                "exit_code": 0,
                "execution_time": 0.05
            }
        elif "python" in command.lower():
            return {
                "stdout": "Script executed successfully\nResult: 42",
                "stderr": "",
                "exit_code": 0,
                "execution_time": 1.2
            }
        else:
            return {
                "stdout": f"Command '{command}' executed",
                "stderr": "",
                "exit_code": 0,
                "execution_time": 0.3
            }

class PlannerAgent:
    """Agent responsible for breaking down tasks into executable steps"""
    
    def __init__(self, llm: ChatOpenAI, memory: ConversationBufferMemory):
        self.llm = llm
        self.memory = memory
        self.system_prompt = """You are a task planning agent. Your job is to break down user tasks into clear, executable steps.

Guidelines:
1. Create numbered, sequential steps
2. Each step should be specific and actionable
3. Consider dependencies between steps
4. Include validation steps where appropriate
5. Format output as a numbered list

Example:
Task: "Create a Python script to analyze data"
Steps:
1. Create a new Python file
2. Import necessary libraries (pandas, numpy)
3. Load data from file
4. Perform basic data analysis
5. Save results to output file
6. Test the script execution
"""
    
    def run(self, task: str) -> List[str]:
        """Break down a task into executable steps"""
        logger.info(f"PlannerAgent processing task: {task}")
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"Break down this task into executable steps:\n{task}")
        ]
        
        try:
            response = self.llm.invoke(messages)
            steps_text = response.content
            
            # Parse steps from response
            steps = []
            for line in steps_text.split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-')):
                    # Clean up the step text
                    step = line.split('.', 1)[-1].strip() if '.' in line else line.strip('- ')
                    if step:
                        steps.append(step)
            
            # Save to memory
            self.memory.save_context(
                {"input": f"Planner task: {task}"},
                {"output": f"Steps: {json.dumps(steps)}"}
            )
            
            logger.info(f"PlannerAgent created {len(steps)} steps")
            return steps
            
        except Exception as e:
            logger.error(f"PlannerAgent error: {e}")
            return [f"Error in planning: {str(e)}"]

class ExecutorAgent:
    """Agent responsible for executing commands in Daytona sandbox"""
    
    def __init__(self, daytona_executor: DaytonaExecutor, memory: ConversationBufferMemory):
        self.daytona = daytona_executor
        self.memory = memory
    
    def run(self, command: str) -> Dict[str, Any]:
        """Execute a command in the Daytona sandbox"""
        logger.info(f"ExecutorAgent executing: {command}")
        
        try:
            result = self.daytona.execute_command(command)
            
            # Save to memory
            self.memory.save_context(
                {"input": f"Executor command: {command}"},
                {"output": f"Result: {json.dumps(result)}"}
            )
            
            logger.info(f"ExecutorAgent completed execution with exit code: {result.get('exit_code', 'unknown')}")
            return result
            
        except Exception as e:
            logger.error(f"ExecutorAgent error: {e}")
            error_result = {
                "stdout": "",
                "stderr": str(e),
                "exit_code": 1,
                "execution_time": 0,
                "error": str(e)
            }
            
            self.memory.save_context(
                {"input": f"Executor command: {command}"},
                {"output": f"Error: {json.dumps(error_result)}"}
            )
            
            return error_result

class ReviewerAgent:
    """Agent responsible for reviewing and validating execution results"""
    
    def __init__(self, llm: ChatOpenAI, memory: ConversationBufferMemory):
        self.llm = llm
        self.memory = memory
        self.system_prompt = """You are a code execution reviewer. Your job is to analyze command execution results and provide feedback.

Guidelines:
1. Check for errors in stderr or non-zero exit codes
2. Validate that stdout contains expected results
3. Identify potential issues or improvements
4. Provide clear, actionable feedback
5. Rate the execution success (SUCCESS/WARNING/ERROR)

Format your response as:
STATUS: [SUCCESS/WARNING/ERROR]
FEEDBACK: [Your detailed feedback]
SUGGESTIONS: [Any suggestions for improvement]
"""
    
    def run(self, command: str, result: Dict[str, Any]) -> Dict[str, str]:
        """Review execution results and provide feedback"""
        logger.info(f"ReviewerAgent reviewing command: {command}")
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"""Review this command execution:

Command: {command}
Result: {json.dumps(result, indent=2)}

Provide your analysis.""")
        ]
        
        try:
            response = self.llm.invoke(messages)
            review_text = response.content
            
            # Parse review response
            review = {
                "status": "UNKNOWN",
                "feedback": review_text,
                "suggestions": ""
            }
            
            # Extract structured information
            for line in review_text.split('\n'):
                if line.startswith('STATUS:'):
                    review["status"] = line.split(':', 1)[1].strip()
                elif line.startswith('FEEDBACK:'):
                    review["feedback"] = line.split(':', 1)[1].strip()
                elif line.startswith('SUGGESTIONS:'):
                    review["suggestions"] = line.split(':', 1)[1].strip()
            
            # Save to memory
            self.memory.save_context(
                {"input": f"Reviewer analyzing: {command}"},
                {"output": f"Review: {json.dumps(review)}"}
            )
            
            logger.info(f"ReviewerAgent completed review with status: {review['status']}")
            return review
            
        except Exception as e:
            logger.error(f"ReviewerAgent error: {e}")
            error_review = {
                "status": "ERROR",
                "feedback": f"Review failed: {str(e)}",
                "suggestions": "Check system configuration and try again"
            }
            
            self.memory.save_context(
                {"input": f"Reviewer analyzing: {command}"},
                {"output": f"Review error: {json.dumps(error_review)}"}
            )
            
            return error_review

class Orchestrator:
    """Main orchestrator that coordinates all agents"""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        
        # Initialize shared memory
        self.memory = ConversationBufferMemory(
            memory_key="history",
            return_messages=True,
            human_prefix="User",
            ai_prefix="Assistant"
        )
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            temperature=config.temperature,
            model_name=config.model_name,
            max_tokens=config.max_tokens,
            openai_api_key=config.openai_api_key
        )
        
        # Initialize Daytona executor
        self.daytona_executor = DaytonaExecutor(
            api_key=config.daytona_api_key,
            server_url=config.daytona_server_url
        )
        
        # Initialize agents
        self.planner = PlannerAgent(self.llm, self.memory)
        self.executor = ExecutorAgent(self.daytona_executor, self.memory)
        self.reviewer = ReviewerAgent(self.llm, self.memory)
        
        logger.info("Orchestrator initialized with all agents")
    
    def run(self, task: str) -> Dict[str, Any]:
        """Execute a complete task using all agents"""
        logger.info(f"Orchestrator starting task: {task}")
        
        try:
            # Step 1: Plan the task
            steps = self.planner.run(task)
            
            if not steps or (len(steps) == 1 and "error" in steps[0].lower()):
                return {
                    "status": "ERROR",
                    "message": "Failed to create execution plan",
                    "steps": steps,
                    "results": [],
                    "memory": self._get_memory_summary()
                }
            
            # Step 2: Execute each step
            execution_results = []
            for i, step in enumerate(steps, 1):
                logger.info(f"Executing step {i}/{len(steps)}: {step}")
                
                # Execute the step
                result = self.executor.run(step)
                
                # Review the result
                review = self.reviewer.run(step, result)
                
                step_result = {
                    "step_number": i,
                    "step_description": step,
                    "execution_result": result,
                    "review": review
                }
                
                execution_results.append(step_result)
                
                # Check if we should stop due to critical error
                if review["status"] == "ERROR" and result.get("exit_code", 0) != 0:
                    logger.warning(f"Critical error in step {i}, stopping execution")
                    break
            
            # Step 3: Compile final response
            final_response = {
                "status": "SUCCESS",
                "message": f"Task completed with {len(execution_results)} steps executed",
                "original_task": task,
                "steps": steps,
                "results": execution_results,
                "memory": self._get_memory_summary(),
                "summary": self._generate_summary(task, execution_results)
            }
            
            logger.info("Orchestrator completed task successfully")
            return final_response
            
        except Exception as e:
            logger.error(f"Orchestrator error: {e}")
            return {
                "status": "ERROR",
                "message": f"Orchestrator failed: {str(e)}",
                "original_task": task,
                "steps": [],
                "results": [],
                "memory": self._get_memory_summary()
            }
    
    def _get_memory_summary(self) -> Dict[str, Any]:
        """Get a summary of the shared memory"""
        try:
            memory_vars = self.memory.load_memory_variables({})
            return {
                "message_count": len(memory_vars.get("history", [])),
                "recent_messages": [str(msg) for msg in memory_vars.get("history", [])[-5:]]
            }
        except Exception as e:
            logger.error(f"Error getting memory summary: {e}")
            return {"error": str(e)}
    
    def _generate_summary(self, task: str, results: List[Dict[str, Any]]) -> str:
        """Generate a summary of the task execution"""
        successful_steps = sum(1 for r in results if r["review"]["status"] in ["SUCCESS", "WARNING"])
        total_steps = len(results)
        
        summary = f"Task: '{task}'\n"
        summary += f"Completed {successful_steps}/{total_steps} steps successfully.\n"
        
        if results:
            summary += "\nStep Results:\n"
            for result in results:
                status_emoji = {"SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌"}.get(
                    result["review"]["status"], "❓"
                )
                summary += f"{status_emoji} Step {result['step_number']}: {result['step_description']}\n"
        
        return summary

def create_agent_system() -> Orchestrator:
    """Factory function to create a configured agent system"""
    
    # Load configuration from environment
    config = AgentConfig(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        daytona_api_key=os.getenv("DAYTONA_API_KEY"),
        daytona_server_url=os.getenv("DAYTONA_SERVER_URL"),
        temperature=float(os.getenv("AGENT_TEMPERATURE", "0.1")),
        model_name=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
        max_tokens=int(os.getenv("MAX_TOKENS", "1000"))
    )
    
    # Validate required configuration
    if not config.openai_api_key:
        raise ValueError("OPENAI_API_KEY is required")
    
    return Orchestrator(config)

def main():
    """Main function for testing the agent system"""
    try:
        # Create the agent system
        orchestrator = create_agent_system()
        
        # Test task
        test_task = "Fetch the current date and list files in the current directory"
        print(f"Testing with task: {test_task}")
        print("-" * 50)
        
        # Run the task
        result = orchestrator.run(test_task)
        
        # Display results
        print(f"Status: {result['status']}")
        print(f"Message: {result['message']}")
        
        if result.get('summary'):
            print(f"\nSummary:\n{result['summary']}")
        
        if result.get('results'):
            print(f"\nDetailed Results:")
            for i, step_result in enumerate(result['results'], 1):
                print(f"\nStep {i}: {step_result['step_description']}")
                print(f"  Exit Code: {step_result['execution_result'].get('exit_code', 'N/A')}")
                print(f"  Output: {step_result['execution_result'].get('stdout', 'No output')}")
                print(f"  Review: {step_result['review']['status']} - {step_result['review']['feedback']}")
        
    except Exception as e:
        logger.error(f"Main execution error: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    main()