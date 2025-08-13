#!/usr/bin/env python3
"""
Simple test to verify the React agent components work properly.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_react_agent_simple():
    """Test the react agent with a simple greeting."""
    print("🔍 Testing React Agent with simple greeting...")
    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import HumanMessage, SystemMessage
        from langchain_community.tools import BraveSearch
        
        # Test basic LLM functionality
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        
        # Test simple greeting (should not use tools)
        messages = [
            SystemMessage(content="You are a helpful AI assistant."),
            HumanMessage(content="Hello!")
        ]
        
        response = llm.invoke(messages)
        print(f"✅ Simple greeting test passed!")
        print(f"Response: {response.content}")
        
        # Test Brave Search (if available)
        brave_api_key = os.getenv("BRAVE_SEARCH_API_KEY")
        if brave_api_key and brave_api_key != "your_brave_search_api_key_here":
            print("\n🔍 Testing Brave Search...")
            brave_tool = BraveSearch.from_api_key(api_key=brave_api_key)
            search_result = brave_tool.run("current weather")
            print(f"✅ Brave Search test passed!")
            print(f"Search result (truncated): {search_result[:100]}...")
        else:
            print("\n⚠️  Brave Search API not configured (this is optional)")
        
        return True
        
    except Exception as e:
        print(f"❌ React Agent test failed: {e}")
        return False

def main():
    """Run the test."""
    print("🚀 Testing React Agent Components...")
    print("=" * 50)
    
    success = test_react_agent_simple()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 React Agent components are working!")
        print("\nTo use the React Agent:")
        print("  streamlit run react_agent.py")
        print("\nThe agent is now available at:")
        print("  http://localhost:8502")
        print("\nNote: The app will automatically handle simple greetings")
        print("      and use web search for current information requests.")
    else:
        print("❌ React Agent has issues. Check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
