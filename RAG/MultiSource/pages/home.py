import streamlit as st
from helpers.qdrantHelper import QdrantHelper
from templates.htmlTemplates import css, bot_template, user_template
from dotenv import load_dotenv
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_ollama import OllamaLLM

import re
import os

load_dotenv("./env/.env")

st.set_page_config(layout="wide")

llmName = os.getenv("LLM_NAME")

def get_conversation_chain(vectorstore):
    llm = OllamaLLM(model=llmName,base_url=os.getenv("LLM_URL"))

    memory = ConversationBufferMemory(
        memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )
    return conversation_chain

def inputchange():
    response = st.session_state.conversation({'question': st.session_state.input})
    st.session_state.chat_history = response['chat_history']

def showResponses():
    if st.session_state.chat_history:
        messages = st.container(height=400)
        regex_pattern = r'<think>[\s\S]*?<\/think>\n\n'
        for i, message in enumerate(st.session_state.chat_history):
            if i % 2 == 0:
                # st.write(user_template.replace(
                # "{{MSG}}", message.content), unsafe_allow_html=True)
                messages.chat_message("user").write(message.content)
            else:
                cleaned_content = re.sub(regex_pattern, '', message.content)
                # st.write(bot_template.replace(
                # "{{MSG}}", cleaned_content), unsafe_allow_html=True)
                messages.chat_message("assistant").write(cleaned_content)
    st.session_state.input = ""

def main():
    
    st.set_page_config(page_title="Chat with multiple PDFs",
                       page_icon=":books:")
    st.write(css, unsafe_allow_html=True)

    with st.spinner("Initialisation...", show_time=True):
        qdrantHelper = QdrantHelper()
        if "qdrantClient" not in st.session_state:
            st.session_state.qdrantClient = qdrantHelper.client

        if "vectorestore" not in st.session_state:
            # create vector store
            st.session_state.vectorstore = qdrantHelper.get_vectorstore(llmName)
        if "conversation" not in st.session_state:
            # create conversation chain
            st.session_state.conversation = get_conversation_chain(st.session_state.vectorstore)
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = None

    st.header("Chat with multiple PDFs")

    if prompt := st.chat_input("Ask a question"):
        response = st.session_state.conversation({'question': prompt})
        st.session_state.chat_history = response['chat_history']
        showResponses()

if __name__ == '__main__':
    main()