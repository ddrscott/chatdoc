import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv()

import unstructured

st.title("Chat Doc")

default_system_message = {"role": "system", "content": "You are a helpful assistant."}

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4o"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "system_message" not in st.session_state:
    st.session_state["system_message"] = "You are a helpful assistant."


with st.sidebar:
    uploaded_file = st.file_uploader("Choose a file, less than 5mb")
    if uploaded_file is not None:
        bytes_data = uploaded_file.getbuffer()
        data = unstructured.partition_api(bytes_data, uploaded_file.name)
        texts = []
        with st.expander("Show parsed text"):
            for elm in data:
                if text := elm.get('text'):
                    texts.append(text)
                    st.write(text)

        joined = '\n'.join(texts)
        st.session_state.system_message = {
            "role": "system",
            "content": f"""Help the user with this document: {uploaded_file.name}\n---\n{joined}\n\n"""
        }
    else:
        st.write("upload a file to start chatting about it.")
        st.session_state.system_message = default_system_message

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    from openai import AzureOpenAI

    llm = AzureOpenAI(
        api_key=os.getenv('OPENAI_API_KEY'),
        api_version="2024-02-01",
        azure_endpoint=os.getenv('OPENAI_API_BASE')
    )

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        messages = [st.session_state.system_message] + st.session_state.messages
        stream = llm.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=messages,
            stream=True,
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})
