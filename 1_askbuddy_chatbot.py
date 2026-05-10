from config import settings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import streamlit as st

llm_google_genai = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite-preview",
    api_key=settings.GEMINI_API_KEY
)
query = [
    {
        "role": "system",
        "content": "Provice direct complete answers using minimum words."
    },
    {"role": "user", "content": "Tell me!!!{query_input}"}
]
prompt = ChatPromptTemplate.from_messages(query)
out = StrOutputParser()

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("Askbuddy Chat Bot")

for message in st.session_state.messages:
    st.chat_message(message["role"]).markdown(message["content"])

query_input = st.chat_input("Enter your question")

if query_input:
    st.session_state.messages.append({"role": "User", "content": query_input})
    st.chat_message("User").markdown(query_input)
    res = (prompt | llm_google_genai | out).invoke(query_input)
    st.session_state.messages.append(
        {"role": "AI", "content": res}
    )
    st.chat_message("AI").markdown(res)
