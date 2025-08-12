from dotenv import load_dotenv
import os
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage
from daytona import Daytona, DaytonaConfig
import json
import re

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DAYTONA_API_KEY = os.getenv("DAYTONA_API_KEY")
DAYTONA_SERVER_URL = os.getenv("DAYTONA_SERVER_URL")

# Validate required environment variables
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is required in .env file")
if not DAYTONA_API_KEY:
    raise ValueError("DAYTONA_API_KEY is required in .env file")
if not DAYTONA_SERVER_URL:
    raise ValueError("DAYTONA_SERVER_URL is required in .env file")

# Initialize LLM & Daytona
llm = ChatOpenAI(
    temperature=0, 
    openai_api_key=OPENAI_API_KEY,
    model="gpt-3.5-turbo"
)

# Initialize Daytona with configuration
try:
    config = DaytonaConfig(api_key=DAYTONA_API_KEY, server_url=DAYTONA_SERVER_URL)
    daytona = Daytona(config=config)
except Exception as e:
    print(f"Warning: Daytona initialization failed: {e}")
    daytona = None

# Shared memory for all agents
memory = ConversationBufferMemory(memory_key="history", return_messages=True)

class PlannerAgent:
    """Breaks down user tasks into executable steps"""
    
    def __init__(self):
        self.llm = llm
        self.memory = memory
    
    def run(self, task):
        """Break down a task into executable steps"""
        prompt = f"""
        You are a task planner. Break down the following task into clear, executable steps.
        Each step should be a single command or action that can be executed.
        
        Task: {task}
        
        Return only the steps, one per line, starting with a number and dash (e.g., "1. - command").
        Keep steps simple and actionable.
        """
        
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            steps = response.content
            
            # Save to memory
            self.memory.save_context(
                {"input": f"Task breakdown for: {task}"},
                {"output": f"Planner generated steps: {steps}"}
            )
            
            return steps
        except Exception as e:
            error_msg = f"Planner error: {str(e)}"
            self.memory.save_context(
                {"input": f"Task breakdown for: {task}"},
                {"output": error_msg}
            )
            return error_msg

class ExecutorAgent:
    """Executes commands in Daytona sandbox"""
    
    def __init__(self):
        self.daytona = daytona
        self.memory = memory
    
    def run(self, command):
        """Execute a command in the Daytona sandbox"""
        if not self.daytona:
            error_msg = "Daytona not available - cannot execute commands"
            self.memory.save_context(
                {"input": f"Execute command: {command}"},
                {"output": error_msg}
            )
            return error_msg
        
        try:
            # Clean the command
            clean_command = command.strip()
            if clean_command.startswith(('1.', '2.', '3.', '4.', '5.')):
                clean_command = clean_command.split('.', 1)[1].strip()
            if clean_command.startswith('-'):
                clean_command = clean_command[1:].strip()
            
            if not clean_command:
                return "Empty command - nothing to execute"
            
            # Execute in Daytona sandbox
            result = self.daytona.execute(clean_command)
            
            # Save to memory
            self.memory.save_context(
                {"input": f"Execute command: {clean_command}"},
                {"output": f"Execution result: {str(result)}"}
            )
            
            return result
        except Exception as e:
            error_msg = f"Execution error: {str(e)}"
            self.memory.save_context(
                {"input": f"Execute command: {command}"},
                {"output": error_msg}
            )
            return error_msg

class ReviewerAgent:
    """Reviews and validates execution outputs"""
    
    def __init__(self):
        self.llm = llm
        self.memory = memory
    
    def run(self, output, original_command=None):
        """Review the output of an execution"""
        prompt = f"""
        You are a code execution reviewer. Review the following output and provide feedback.
        
        Command executed: {original_command or 'Unknown'}
        Output: {output}
        
        Please provide:
        1. Is the output valid and complete?
        2. Any errors or warnings?
        3. Suggestions for improvement?
        
        Keep your review concise and actionable.
        """
        
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            review = response.content
            
            # Save to memory
            self.memory.save_context(
                {"input": f"Review output for: {original_command or 'Unknown'}"},
                {"output": f"Review: {review}"}
            )
            
            return review
        except Exception as e:
            error_msg = f"Review error: {str(e)}"
            self.memory.save_context(
                {"input": f"Review output for: {original_command or 'Unknown'}"},
                {"output": error_msg}
            )
            return error_msg

class Orchestrator:
    """Coordinates all agents and manages the workflow"""
    
    def __init__(self):
        self.planner = PlannerAgent()
        self.executor = ExecutorAgent()
        self.reviewer = ReviewerAgent()
        self.memory = memory
    
    def run(self, task):
        """Execute the complete workflow for a given task"""
        print(f"🎯 Starting task: {task}")
        print("-" * 50)
        
        # Step 1: Plan
        print("📋 Planning task...")
        steps = self.planner.run(task)
        print(f"Planner generated steps:\n{steps}")
        print("-" * 50)
        
        # Step 2: Execute each step
        step_results = []
        step_lines = [line.strip() for line in steps.split('\n') if line.strip()]
        
        for i, step in enumerate(step_lines, 1):
            print(f"⚡ Executing step {i}: {step}")
            
            # Execute the step
            result = self.executor.run(step)
            step_results.append({
                'step': step,
                'result': result
            })
            print(f"Result: {result}")
            
            # Review the result
            print(f"🔍 Reviewing step {i}...")
            review = self.reviewer.run(result, step)
            print(f"Review: {review}")
            print("-" * 50)
        
        # Step 3: Compile final response
        print("📝 Compiling final response...")
        final_response = self._compile_final_response(task, step_results)
        
        # Save final result to memory
        self.memory.save_context(
            {"input": f"Complete task: {task}"},
            {"output": f"Final result: {final_response}"}
        )
        
        print("✅ Task completed!")
        return final_response
    
    def _compile_final_response(self, task, step_results):
        """Compile a coherent final response from all step results"""
        prompt = f"""
        You are a task orchestrator. Compile a final response based on the original task and all step results.
        
        Original Task: {task}
        
        Step Results:
        {json.dumps(step_results, indent=2)}
        
        Provide a clear, coherent summary that:
        1. Confirms the task was completed
        2. Summarizes the key results
        3. Highlights any important findings or errors
        4. Is written in a professional, helpful tone
        
        Keep the response concise but informative.
        """
        
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            return response.content
        except Exception as e:
            return f"Error compiling final response: {str(e)}"
    
    def get_memory(self):
        """Get the current conversation memory"""
        return self.memory.load_memory_variables({})["history"]

def main():
    """Main function to demonstrate the agent system"""
    print("🤖 PRP: LangChain + Daytona Agent System")
    print("=" * 50)
    
    # Example task
    task = "Fetch the current date and list files in the current directory"
    
    try:
        orchestrator = Orchestrator()
        result = orchestrator.run(task)
        
        print("\n🎉 Final Result:")
        print("=" * 50)
        print(result)
        
        print("\n📚 Memory History:")
        print("=" * 50)
        memory_content = orchestrator.get_memory()
        for msg in memory_content:
            if hasattr(msg, 'content'):
                print(f"{type(msg).__name__}: {msg.content[:100]}...")
            else:
                print(f"{type(msg).__name__}: {str(msg)[:100]}...")
                
    except Exception as e:
        print(f"❌ System error: {str(e)}")

if __name__ == "__main__":
    main()