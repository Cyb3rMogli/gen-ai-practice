from config import settings
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langgraph.checkpoint.memory import MemorySaver
from langchain.tools import tool
from langchain_core.messages.ai import AIMessageChunk
import streamlit as st
from datetime import date


@tool
def date_today():
    '''
    Function returns curent system date.
    Args: N/A
    Return:{"date": "yyyy-mm-dd"}
    '''
    return {"date": str(date.today())}


llm = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=settings.GROQ_API_KEY,
    streaming=True)

search = DuckDuckGoSearchAPIWrapper()
tools = [search.run, date_today]
mem = MemorySaver()
sys_prompt = '''You are a news bot.
Check current date and search the internet for up to date information.
Only answer questions about yourself or news and current affairs.'''
agent = create_agent(
    model=llm,
    tools=tools,
    checkpointer=mem,
    system_prompt=sys_prompt
)

# ### Web Interface ###
if "memory" not in st.session_state:
    st.session_state.memory = mem
if "history" not in st.session_state:
    st.session_state.history = []

st.subheader("News and Current Affairs Chatbot")
for msg in st.session_state.history:
    st.chat_message(msg["role"]).markdown(msg["content"])

query = st.chat_input()
if query:
    st.session_state.history.append({"role": "user", "content": query})
    st.chat_message("user").markdown(query)

    res = agent.stream(
        {
            "messages": [st.session_state.history[-1]]
        },
        {
            "configurable": {"thread_id": "1"}
        },
        stream_mode="messages"
    )
    ai_container = st.chat_message("ai")
    with ai_container:
        space = st.empty()
        message = ""
        for chunk in res:
            if isinstance(chunk[0], AIMessageChunk) and chunk[0].content:
                message += chunk[0].content
                space.write(message)

        st.session_state.history.append({"role": "ai", "content": message})
