from typing import Set

from backend.core import run_llm
import streamlit as st
from streamlit_chat import message
import time
import random

#st.header("LangChain Documentation Helper Bot")
st.set_page_config(page_title="Chat with your documentation", page_icon=" :page_with_curl:")
st.markdown("<h1 style='text-align: center;'>Langchain Documentation Helper</h1>", unsafe_allow_html=True)

random_number1 = str(random.random())
prompt = st.text_input("Prompt", placeholder="Enter prompt here..", key="user_input")

def reset_conversation():
    st.session_state["user_prompt_history"] = []
    st.session_state["chat_answers_history"] = []
    st.session_state["chat_history"] = []

with st.sidebar:
    with st.spinner("Loading..."):
        time.sleep(1)
    st.success("Done!")
    random_number = str(random.random())
    st.sidebar.button('New Chat', on_click=reset_conversation, key="button1")

if "user_prompt_history" not in st.session_state:
    st.session_state["user_prompt_history"] = []

if "chat_answers_history" not in st.session_state:
    st.session_state["chat_answers_history"] = []

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []


def create_sources_string(source_urls: Set[str]) -> str:
    if not source_urls:
        return ""
    sources_list = list(source_urls)
    sources_list.sort()
    sources_string = "sources:\n"
    for i, source in enumerate(sources_list):
        sources_string += f"{i+1}. {source}\n"
    return sources_string


if prompt:
    with st.spinner("Generating response.."):
        generated_response = run_llm(
            query=prompt, chat_history=st.session_state["chat_history"]
        )
        sources = set(
            [doc.metadata["source"] for doc in generated_response["source_documents"]]
        )

        formatted_response = (
            f"{generated_response['answer']} \n\n {create_sources_string(sources)}"
        )

        st.session_state["user_prompt_history"].append(prompt)
        st.session_state["chat_answers_history"].append(formatted_response)
        st.session_state["chat_history"].append((prompt, generated_response["answer"]))

if st.session_state["chat_answers_history"]:
    for generated_response, user_query in zip(
        st.session_state["chat_answers_history"],
        st.session_state["user_prompt_history"],
    ):
        message(user_query, is_user=True)
        message(generated_response)