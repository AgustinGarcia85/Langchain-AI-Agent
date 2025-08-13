#!/usr/bin/env python3
"""
Test script to demonstrate both AI agents are working properly.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_agent_system():
    """Test the basic agent system."""
    print("🤖 Testing Agent System...")
    try:
        from agent_system import Orchestrator
        
        # Create and run orchestrator
        orchestrator = Orchestrator()
        result = orchestrator.run("Show current directory and list Python files")
        print("✅ Agent System is working!")
        print(f"Result: {result[:100]}...")
        return True
    except Exception as e:
        print(f"❌ Agent System failed: {e}")
        return False

def test_react_agent_components():
    """Test the react agent components without Streamlit."""
    print("\n🔍 Testing React Agent components...")
    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import HumanMessage, SystemMessage
        
        # Test basic LLM functionality
        openai_key = os.getenv("OPENAI_API_KEY")
        brave_key = os.getenv("BRAVE_SEARCH_API_KEY")
        
        if not openai_key or openai_key.startswith("your_"):
            print("⚠️  OpenAI API key not configured properly")
            return False
            
        if not brave_key or brave_key == "your_brave_search_api_key_here":
            print("⚠️  Brave Search API key not configured (this is optional)")
        
        # Test basic chat functionality
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        messages = [
            SystemMessage(content="You are a helpful assistant."),
            HumanMessage(content="Hello! Just say 'Hello back' to confirm you're working.")
        ]
        
        response = llm.invoke(messages)
        print("✅ React Agent LLM is working!")
        print(f"Response: {response.content}")
        return True
        
    except Exception as e:
        print(f"❌ React Agent components failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Testing AI Agents...")
    print("=" * 50)
    
    agent_system_ok = test_agent_system()
    react_agent_ok = test_react_agent_components()
    
    print("\n" + "=" * 50)
    if agent_system_ok and react_agent_ok:
        print("🎉 All agents are working correctly!")
        print("\nTo use the agents:")
        print("1. Basic Agent System: python agent_system.py")
        print("2. React Agent UI: streamlit run react_agent.py")
        print("\nFor the React Agent, you can get API keys from:")
        print("- OpenAI: https://platform.openai.com/account/api-keys")
        print("- Brave Search: https://brave.com/search/api/")
        print("- LangSmith: https://smith.langchain.com/")
    else:
        print("❌ Some agents have issues. Check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
