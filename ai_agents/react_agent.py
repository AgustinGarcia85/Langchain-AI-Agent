import os
from dotenv import load_dotenv
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import chain
from langsmith import traceable
from langchain_community.tools import BraveSearch
from langchain.agents import AgentExecutor, create_react_agent
from langchain import hub

# Load environment variables from .env file
load_dotenv()

# Set LangSmith tracing environment variables (only if API key is properly configured)
langsmith_key = os.getenv("LANGSMITH_API_KEY", "")
if langsmith_key and langsmith_key != "your_langsmith_api_key_here":
    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGSMITH_API_KEY"] = langsmith_key
else:
    os.environ["LANGSMITH_TRACING"] = "false"
    print("ℹ️  LangSmith tracing disabled (API key not configured)")
    
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")

# Ensure Brave Search API key is loaded from environment
brave_api_key = os.getenv("BRAVE_SEARCH_API_KEY")
if not brave_api_key or brave_api_key == "your_brave_search_api_key_here":
    print("⚠️  BRAVE_SEARCH_API_KEY not found or not configured.")
    print("   Please get your API key from https://brave.com/search/api/")
    print("   and add it to your .env file:")
    print("   BRAVE_SEARCH_API_KEY=your_actual_api_key_here")
    print("\n   Running without web search capabilities for now...")
    brave_tool = None
else:
    # Initialize Brave Search tool for web search capabilities
    brave_tool = BraveSearch.from_api_key(api_key=brave_api_key)

# Define system prompt for the agent to guide its behavior
system_prompt = """You are a helpful assistant that can search the web for information.

Instructions:
1. For simple greetings or conversations that don't require current information, respond directly without using tools
2. Only use the search tool when users ask about:
   - Current events, news, or time-sensitive information
   - Weather conditions
   - Recent developments or updates
   - Information that changes frequently

For general questions or greetings, respond naturally without searching."""

# Create a React agent using LangChain's ReAct framework
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)  # Use cheaper model for better response

# Create tools list based on available APIs
tools = [brave_tool] if brave_tool else []

if tools:
    # Use the standard React prompt but with better instructions
    prompt = hub.pull("hwchase17/react")
    
    agent = create_react_agent(llm, tools, prompt)
    agent_executor = AgentExecutor.from_agent_and_tools(
        agent=agent, 
        tools=tools, 
        verbose=False,  # Reduce verbosity
        handle_parsing_errors=True,
        max_iterations=2,  # Keep it simple for basic conversations
        early_stopping_method="generate",
        return_intermediate_steps=False  # Don't return intermediate steps
    )
else:
    # Fallback for when no tools are available
    agent_executor = None

# Streamlit UI setup
st.set_page_config(page_title="React Agent with LangSmith Tracking")
st.title("🦜🔗 React Agent (LangChain + LangSmith)")

# Display API key status
st.sidebar.title("Configuration Status")
if brave_tool:
    st.sidebar.success("✅ Brave Search API configured")
else:
    st.sidebar.warning("⚠️ Brave Search API not configured")

if os.environ.get("LANGSMITH_TRACING") == "true":
    st.sidebar.success("✅ LangSmith tracing enabled")
else:
    st.sidebar.info("ℹ️ LangSmith tracing disabled")

# Initialize chat history and input state in Streamlit session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display chat history using Streamlit's chat interface
for msg in st.session_state.chat_history:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.markdown(msg.content)
    else:
        with st.chat_message("assistant"):
            st.markdown(msg.content)

# Chat input that automatically clears after submission
if prompt := st.chat_input("Type your message here..."):
    # Add user message to chat history and display it
    st.session_state.chat_history.append(HumanMessage(content=prompt))
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                if agent_executor:
                    # Smart agent execution with fallback
                    def smart_agent_response(query):
                        # Simple heuristics to determine if we need web search
                        search_keywords = ['weather', 'news', 'current', 'today', 'latest', 'recent', 'what is happening', 'stock price', 'temperature']
                        greeting_keywords = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening', 'how are you']
                        
                        query_lower = query.lower()
                        
                        # Check if it's a simple greeting
                        if any(keyword in query_lower for keyword in greeting_keywords) and len(query.split()) <= 5:
                            return "Hello! I'm your AI assistant. I can help answer questions and search for current information when needed. How can I assist you today?"
                        
                        # Check if it needs web search
                        needs_search = any(keyword in query_lower for keyword in search_keywords)
                        
                        if needs_search:
                            try:
                                response = agent_executor.invoke({"input": query})
                                return response.get("output", "I couldn't find the information you requested.")
                            except Exception as e:
                                if "iteration limit" in str(e).lower():
                                    return f"I tried to search for information about '{query}' but encountered some complexity. Could you please be more specific about what you'd like to know?"
                                return f"I encountered an issue while searching: {str(e)}"
                        else:
                            # For general questions, use the LLM directly
                            try:
                                messages = [
                                    SystemMessage(content="You are a helpful AI assistant. Provide helpful, accurate responses to user questions."),
                                    HumanMessage(content=query)
                                ]
                                response = llm.invoke(messages)
                                return response.content
                            except Exception as e:
                                return f"I encountered an error: {str(e)}"
                    
                    # Apply tracing if LangSmith is enabled
                    if os.environ.get("LANGSMITH_TRACING") == "true":
                        smart_agent_response = traceable(smart_agent_response)
                        
                    agent_response = smart_agent_response(prompt)
                else:
                    # Fallback when no tools are available
                    messages = [
                        SystemMessage(content="You are a helpful assistant. Note: Web search is not available due to missing API keys."),
                        HumanMessage(content=prompt)
                    ]
                    response = llm.invoke(messages)
                    agent_response = response.content
                    
            except Exception as e:
                agent_response = f"Sorry, I encountered an error: {str(e)}"
                
            # Display and add agent response to chat history
            st.markdown(agent_response)
            st.session_state.chat_history.append(AIMessage(content=agent_response))

# Instructions
with st.expander("ℹ️ How to use"):
    st.markdown("""
    - **Simple questions**: Just ask normally, I'll respond directly
    - **Current information**: Ask about weather, news, or recent events and I'll search the web
    - **Examples**: 
      - "Hello!" → Direct response
      - "What's the weather in New York?" → Web search
      - "Latest news about AI" → Web search
    """)

# Clear chat button
if st.button("🗑️ Clear Chat"):
    st.session_state.chat_history = []
    st.rerun()
