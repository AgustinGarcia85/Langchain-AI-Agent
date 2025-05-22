import os
from dotenv import load_dotenv
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.runnables import chain
from langsmith import traceable
from langchain_community.tools import BraveSearch
from langchain.agents import AgentExecutor, create_react_agent
from langchain import hub

# Load environment variables from .env file
load_dotenv()

# Set LangSmith tracing environment variables
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY", "")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")

# Ensure Brave Search API key is loaded from environment
brave_api_key = os.getenv("BRAVE_SEARCH_API_KEY")
if not brave_api_key:
    raise ValueError("BRAVE_SEARCH_API_KEY not found in environment. Please add it to your .env file.")

# Initialize Brave Search tool for web search capabilities
brave_tool = BraveSearch.from_api_key(api_key=brave_api_key)

# Define system prompt for the agent to guide its behavior
system_prompt = """You are a helpful assistant that can search the web for information.
When users ask about current information like weather, news, or other real-time data, 
use the search tool to find the most up-to-date information. Always use the search tool
for queries about current conditions or time-sensitive information."""

# Create a React agent using LangChain's ReAct framework
llm = ChatOpenAI(model="gpt-4o", temperature=0)
prompt = hub.pull("hwchase17/react")
agent = create_react_agent(llm, [brave_tool], prompt)
agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent, 
    tools=[brave_tool], 
    verbose=True
)

# Streamlit UI setup
st.set_page_config(page_title="React Agent with LangSmith Tracking")
st.title("🦜🔗 React Agent (LangChain + LangSmith)")

# Initialize chat history in Streamlit session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# User input text box
user_input = st.text_input("You:", "Hello, agent!")

# Handle user input and agent response on button click
if st.button("Send"):
    st.session_state.chat_history.append(HumanMessage(content=user_input))
    with st.spinner("Thinking..."):
        # Track agent execution with LangSmith
        @traceable
        def tracked_react_agent(query):
            response = agent_executor.invoke({"input": query})
            return response["output"]
            
        agent_response = tracked_react_agent(user_input)
        st.session_state.chat_history.append(AIMessage(content=agent_response))

# Display chat history in the UI
for msg in st.session_state.chat_history:
    if isinstance(msg, HumanMessage):
        st.markdown(f"**You:** {msg.content}")
    else:
        st.markdown(f"**Agent:** {msg.content}")
