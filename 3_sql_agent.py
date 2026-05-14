from config import settings
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langgraph.checkpoint.memory import InMemorySaver
import streamlit as st

db = SQLDatabase.from_uri('sqlite:///taksk.db')
db.run(
    '''Create table if not exists tasks (
    task_id integer primary key autoincrement,
    title text not null,
    description text,
    status text check (status in ('pending', 'in_progress', 'complete'))
    default 'pending',
    created_at timestamp default current_timestamp);'''
)

model = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=settings.GROQ_API_KEY,
    streaming=True)

toolkit = SQLDatabaseToolkit(db=db, llm=model)
tools = toolkit.get_tools()
mem = InMemorySaver()

system_prompt = '''
You are a task management bot that interacts with sql database table "tasks".
Rules:
1. Limit select queries to max 10 results, order by created date, descending,
2. Confirm with select query after create/update/delete.
3. If list of tasks is requested, present it in tabulare format.

CRUD operations:
Create: Insert into tasks(title, description)
Read: Select * from tasks where ... Limit 10
Update: Update tasks set status=? where task_id=? or title=?
Delete: Delete from tasks where task_id=? or title=?

Table Schema (task_id, title, description,
status('pending', 'in_progress', 'complete'), created_at)
'''


@st.cache_resource
def get_agent():
    return create_agent(
        model=model,
        tools=tools,
        checkpointer=mem,
        system_prompt=system_prompt
    )


agent = get_agent()
st.subheader("Task Management Bot")
query = st.chat_input()
if query:
    st.chat_message("user").markdown(query)

with st.chat_message("ai"):
    with st.spinner("Working On It..."):
        if query:
            response = agent.invoke(
                {"messages": {"role": "user", "content": query}},
                {"configurable": {"thread_id": "1"}}
            )
            result = response["messages"][-1].content
            st.markdown(result)
        else:
            st.markdown("Hi! What's your plan?")
