# React Agent (LangChain + LangSmith)

This project implements a web-search-enabled AI assistant using the LangChain ReAct agent framework, Streamlit for the UI, and LangSmith for tracing and observability.

## Features
- Web search via Brave Search API
- Conversational interface powered by Streamlit
- LangSmith tracing for agent runs
- Secure environment variable management

## Setup
1. **Clone the repository**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Create a `.env` file** in the `ai_agents` directory with the following variables:
   ```env
   OPENAI_API_KEY=your-openai-key
   LANGSMITH_API_KEY=your-langsmith-key
   BRAVE_SEARCH_API_KEY=your-brave-search-key
   ```
4. **Run the app**:
   ```bash
   streamlit run react_agent.py
   ```

## Usage
- Enter your query in the text box and click "Send".
- The agent will use web search for real-time or current information queries.
- All agent runs are tracked with LangSmith for observability.

## Security
- **Never commit your `.env` file.** It is excluded via `.gitignore`.
- API keys are loaded securely from environment variables.

## Requirements
- Python 3.8+
- See `requirements.txt` for package dependencies.

## License
MIT 
