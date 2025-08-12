#!/usr/bin/env python3
"""
Example usage of the Multi-Agent System

This script demonstrates how to use the agent system for various tasks:
1. Simple file operations
2. Data analysis tasks
3. Python script creation and execution
4. Error handling scenarios

Run this script to see the agent system in action.
"""

import os
import json
import time
from agent_system import create_agent_system, AgentConfig, Orchestrator

def print_separator(title: str):
    """Print a formatted separator"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_results(result: dict):
    """Pretty print the orchestrator results"""
    print(f"\n📊 Task Status: {result['status']}")
    print(f"📝 Message: {result['message']}")
    
    if result.get('summary'):
        print(f"\n📋 Summary:")
        print(result['summary'])
    
    if result.get('results'):
        print(f"\n🔍 Detailed Step Results:")
        for i, step_result in enumerate(result['results'], 1):
            status_emoji = {"SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌"}.get(
                step_result['review']['status'], "❓"
            )
            print(f"\n{status_emoji} Step {i}: {step_result['step_description']}")
            print(f"   Exit Code: {step_result['execution_result'].get('exit_code', 'N/A')}")
            
            stdout = step_result['execution_result'].get('stdout', '')
            if stdout:
                print(f"   Output: {stdout[:100]}{'...' if len(stdout) > 100 else ''}")
            
            stderr = step_result['execution_result'].get('stderr', '')
            if stderr:
                print(f"   Error: {stderr[:100]}{'...' if len(stderr) > 100 else ''}")
            
            print(f"   Review: {step_result['review']['feedback'][:100]}{'...' if len(step_result['review']['feedback']) > 100 else ''}")
    
    print("\n" + "-"*60)

def example_1_basic_operations():
    """Example 1: Basic file operations"""
    print_separator("Example 1: Basic File Operations")
    
    try:
        orchestrator = create_agent_system()
        
        task = "Get the current date and time, then list all files in the current directory"
        print(f"🎯 Task: {task}")
        
        result = orchestrator.run(task)
        print_results(result)
        
    except Exception as e:
        print(f"❌ Error in Example 1: {e}")

def example_2_python_analysis():
    """Example 2: Python data analysis task"""
    print_separator("Example 2: Python Data Analysis")
    
    try:
        orchestrator = create_agent_system()
        
        task = """Create a Python script that:
1. Generates sample data (list of numbers)
2. Calculates basic statistics (mean, median, max, min)
3. Prints the results
4. Saves the statistics to a file"""
        
        print(f"🎯 Task: {task}")
        
        result = orchestrator.run(task)
        print_results(result)
        
    except Exception as e:
        print(f"❌ Error in Example 2: {e}")

def example_3_web_development():
    """Example 3: Simple web development task"""
    print_separator("Example 3: Web Development Task")
    
    try:
        orchestrator = create_agent_system()
        
        task = """Create a simple HTML page with:
1. A title "My Agent-Generated Page"
2. A header with current date
3. A list of sample items
4. Basic CSS styling
5. Save it as index.html"""
        
        print(f"🎯 Task: {task}")
        
        result = orchestrator.run(task)
        print_results(result)
        
    except Exception as e:
        print(f"❌ Error in Example 3: {e}")

def example_4_system_info():
    """Example 4: System information gathering"""
    print_separator("Example 4: System Information Gathering")
    
    try:
        orchestrator = create_agent_system()
        
        task = """Gather system information:
1. Check current working directory
2. List environment variables (first 5)
3. Check disk usage
4. Show current user
5. Display system uptime"""
        
        print(f"🎯 Task: {task}")
        
        result = orchestrator.run(task)
        print_results(result)
        
    except Exception as e:
        print(f"❌ Error in Example 4: {e}")

def example_5_error_handling():
    """Example 5: Error handling demonstration"""
    print_separator("Example 5: Error Handling Demonstration")
    
    try:
        orchestrator = create_agent_system()
        
        task = """Demonstrate error handling by:
1. Trying to access a non-existent file
2. Running an invalid command
3. Creating a Python script with syntax errors
4. Attempting to recover from errors"""
        
        print(f"🎯 Task: {task}")
        
        result = orchestrator.run(task)
        print_results(result)
        
    except Exception as e:
        print(f"❌ Error in Example 5: {e}")

def interactive_mode():
    """Interactive mode for custom tasks"""
    print_separator("Interactive Mode")
    
    try:
        orchestrator = create_agent_system()
        
        print("🤖 Welcome to Interactive Agent Mode!")
        print("Enter your tasks and the agent system will break them down and execute them.")
        print("Type 'quit' to exit.\n")
        
        while True:
            task = input("🎯 Enter your task: ").strip()
            
            if task.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not task:
                print("Please enter a valid task.")
                continue
            
            print(f"\n🔄 Processing task: {task}")
            print("This may take a moment...\n")
            
            start_time = time.time()
            result = orchestrator.run(task)
            end_time = time.time()
            
            print_results(result)
            print(f"⏱️  Execution time: {end_time - start_time:.2f} seconds")
            
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error in Interactive Mode: {e}")

def demonstrate_memory():
    """Demonstrate shared memory across tasks"""
    print_separator("Memory Demonstration")
    
    try:
        orchestrator = create_agent_system()
        
        print("🧠 Demonstrating shared memory across multiple tasks...")
        
        # Task 1: Create some data
        task1 = "Create a file called 'memory_test.txt' with the content 'Hello from Agent System!'"
        print(f"\n🎯 Task 1: {task1}")
        result1 = orchestrator.run(task1)
        print(f"✅ Task 1 Status: {result1['status']}")
        
        # Task 2: Read the data (should remember previous task)
        task2 = "Read the content of 'memory_test.txt' and display it"
        print(f"\n🎯 Task 2: {task2}")
        result2 = orchestrator.run(task2)
        print(f"✅ Task 2 Status: {result2['status']}")
        
        # Show memory summary
        memory_summary = result2.get('memory', {})
        print(f"\n🧠 Memory Summary:")
        print(f"   Total messages in memory: {memory_summary.get('message_count', 0)}")
        
        if memory_summary.get('recent_messages'):
            print("   Recent memory entries:")
            for i, msg in enumerate(memory_summary['recent_messages'][-3:], 1):
                print(f"     {i}. {str(msg)[:80]}...")
        
    except Exception as e:
        print(f"❌ Error in Memory Demonstration: {e}")

def main():
    """Main function to run all examples"""
    print("🚀 Multi-Agent System Examples")
    print("This script demonstrates the capabilities of the agent system.")
    print("Make sure you have set up your .env file with the required API keys.")
    
    # Check if environment is set up
    if not os.getenv('OPENAI_API_KEY'):
        print("\n❌ Error: OPENAI_API_KEY not found in environment variables.")
        print("Please create a .env file with your API keys. See .env.sample for reference.")
        return
    
    examples = [
        ("1", "Basic Operations", example_1_basic_operations),
        ("2", "Python Analysis", example_2_python_analysis),
        ("3", "Web Development", example_3_web_development),
        ("4", "System Information", example_4_system_info),
        ("5", "Error Handling", example_5_error_handling),
        ("6", "Memory Demo", demonstrate_memory),
        ("i", "Interactive Mode", interactive_mode),
    ]
    
    print("\n📋 Available Examples:")
    for key, name, _ in examples:
        print(f"  {key}. {name}")
    print("  a. Run all examples")
    print("  q. Quit")
    
    while True:
        choice = input("\n🎯 Select an example (1-6, i, a, q): ").strip().lower()
        
        if choice == 'q':
            print("👋 Goodbye!")
            break
        elif choice == 'a':
            # Run all examples except interactive
            for key, name, func in examples[:-1]:  # Exclude interactive mode
                print(f"\n🔄 Running {name}...")
                func()
                time.sleep(2)  # Brief pause between examples
            break
        elif choice == 'i':
            interactive_mode()
            break
        else:
            # Find and run specific example
            example_found = False
            for key, name, func in examples:
                if choice == key:
                    func()
                    example_found = True
                    break
            
            if not example_found:
                print("❌ Invalid choice. Please select a valid option.")

if __name__ == "__main__":
    main()