#!/usr/bin/env python3
"""
Demo script for the PRP: LangChain + Daytona Agent System

This script demonstrates various capabilities of the agent system
including different task types and individual agent usage.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check if required environment variables are set
required_vars = ['OPENAI_API_KEY', 'DAYTONA_API_KEY', 'DAYTONA_SERVER_URL']
missing_vars = [var for var in required_vars if not os.getenv(var)]

if missing_vars:
    print("❌ Missing required environment variables:")
    for var in missing_vars:
        print(f"   - {var}")
    print("\nPlease set up your .env file with the required API keys.")
    print("You can copy .env.example to .env and fill in your actual keys.")
    sys.exit(1)

# Import the agent system
try:
    from agent_system import (
        PlannerAgent, 
        ExecutorAgent, 
        ReviewerAgent, 
        Orchestrator
    )
    print("✅ Agent system imported successfully!")
except ImportError as e:
    print(f"❌ Failed to import agent system: {e}")
    print("Make sure all dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)

def demo_individual_agents():
    """Demonstrate individual agent capabilities"""
    print("\n" + "="*60)
    print("🤖 INDIVIDUAL AGENT DEMONSTRATION")
    print("="*60)
    
    # Initialize agents
    planner = PlannerAgent()
    executor = ExecutorAgent()
    reviewer = ReviewerAgent()
    
    # Demo 1: Planning a task
    print("\n📋 Demo 1: Task Planning")
    print("-" * 40)
    task = "Set up a Python development environment"
    print(f"Task: {task}")
    
    try:
        steps = planner.run(task)
        print(f"Planned steps:\n{steps}")
    except Exception as e:
        print(f"❌ Planning failed: {e}")
    
    # Demo 2: Command execution
    print("\n⚡ Demo 2: Command Execution")
    print("-" * 40)
    command = "echo 'Hello from Daytona sandbox!'"
    print(f"Command: {command}")
    
    try:
        result = executor.run(command)
        print(f"Result: {result}")
    except Exception as e:
        print(f"❌ Execution failed: {e}")
    
    # Demo 3: Output review
    print("\n🔍 Demo 3: Output Review")
    print("-" * 40)
    sample_output = "Hello from Daytona sandbox!"
    print(f"Output to review: {sample_output}")
    
    try:
        review = reviewer.run(sample_output, command)
        print(f"Review: {review}")
    except Exception as e:
        print(f"❌ Review failed: {e}")

def demo_orchestrated_workflow():
    """Demonstrate the complete orchestrated workflow"""
    print("\n" + "="*60)
    print("🎯 ORCHESTRATED WORKFLOW DEMONSTRATION")
    print("="*60)
    
    # Initialize orchestrator
    orchestrator = Orchestrator()
    
    # Demo tasks
    demo_tasks = [
        "Get current system information and list running processes",
        "Create a test file and display its contents",
        "Check network connectivity and current working directory"
    ]
    
    for i, task in enumerate(demo_tasks, 1):
        print(f"\n🔄 Demo Workflow {i}: {task}")
        print("-" * 50)
        
        try:
            result = orchestrator.run(task)
            print(f"\n✅ Final Result: {result}")
        except Exception as e:
            print(f"❌ Workflow failed: {e}")
        
        print("\n" + "="*50)

def demo_custom_tasks():
    """Demonstrate custom task creation"""
    print("\n" + "="*60)
    print("🎨 CUSTOM TASK DEMONSTRATION")
    print("="*60)
    
    orchestrator = Orchestrator()
    
    # Interactive custom task
    print("\n💡 Enter a custom task to execute:")
    print("(Examples: 'Install a package', 'Check disk usage', 'Create a backup')")
    
    try:
        custom_task = input("\nYour task: ").strip()
        if custom_task:
            print(f"\n🚀 Executing custom task: {custom_task}")
            result = orchestrator.run(custom_task)
            print(f"\n🎉 Custom task result: {result}")
        else:
            print("No task provided, skipping custom task demo.")
    except KeyboardInterrupt:
        print("\n\n⏹️  Custom task demo interrupted.")
    except Exception as e:
        print(f"❌ Custom task failed: {e}")

def demo_memory_inspection():
    """Demonstrate memory inspection capabilities"""
    print("\n" + "="*60)
    print("🧠 MEMORY INSPECTION DEMONSTRATION")
    print("="*60)
    
    orchestrator = Orchestrator()
    
    # Run a simple task to populate memory
    print("Running a simple task to populate memory...")
    try:
        orchestrator.run("Show current date")
        
        # Inspect memory
        print("\n📚 Current Memory Contents:")
        print("-" * 40)
        memory_content = orchestrator.get_memory()
        
        for i, msg in enumerate(memory_content, 1):
            if hasattr(msg, 'content'):
                content = msg.content[:100] + "..." if len(str(msg.content)) > 100 else msg.content
                print(f"{i}. {type(msg).__name__}: {content}")
            else:
                content = str(msg)[:100] + "..." if len(str(msg)) > 100 else str(msg)
                print(f"{i}. {type(msg).__name__}: {content}")
                
    except Exception as e:
        print(f"❌ Memory inspection failed: {e}")

def main():
    """Main demo function"""
    print("🚀 PRP: LangChain + Daytona Agent System Demo")
    print("=" * 60)
    print("This demo showcases the capabilities of the modular AI agent system.")
    print("Make sure you have valid API keys in your .env file.")
    
    # Check system status
    print(f"\n🔍 System Status:")
    print(f"   OpenAI API Key: {'✅ Set' if os.getenv('OPENAI_API_KEY') else '❌ Missing'}")
    print(f"   Daytona API Key: {'✅ Set' if os.getenv('DAYTONA_API_KEY') else '❌ Missing'}")
    print(f"   Daytona Server: {'✅ Set' if os.getenv('DAYTONA_SERVER_URL') else '❌ Missing'}")
    
    if missing_vars:
        print("\n⚠️  Some required environment variables are missing.")
        print("The demo will continue but may fail for certain operations.")
    
    try:
        # Run demos
        demo_individual_agents()
        demo_orchestrated_workflow()
        demo_memory_inspection()
        demo_custom_tasks()
        
        print("\n" + "="*60)
        print("🎉 Demo completed successfully!")
        print("="*60)
        print("\n💡 Tips for further exploration:")
        print("   - Modify the demo tasks in this script")
        print("   - Create your own custom agent workflows")
        print("   - Experiment with different task types")
        print("   - Check the AGENT_SYSTEM_README.md for detailed usage")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user.")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        print("Check your API keys and network connectivity.")

if __name__ == "__main__":
    main()