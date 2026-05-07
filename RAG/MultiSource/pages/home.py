import streamlit as st
from helpers.qdrantHelper import QdrantHelper
from templates.htmlTemplates import css
from dotenv import load_dotenv
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage, AIMessage
from helpers.confidenceRetriever import ConfidenceRetriever

import re
import os
import time
import requests

load_dotenv("./env/.env")

st.set_page_config(page_title="Knowledge Base", layout="wide")

llmName = os.getenv("LLM_NAME")
llmUrl = os.getenv("LLM_URL")

def get_available_models():
    try:
        response = requests.get(f"{llmUrl}/api/tags")
        if response.status_code == 200:
            models_data = response.json()
            if models_data.get("models"):
                return sorted([model["name"] for model in models_data["models"]])
        return [llmName]
    except Exception as e:
        st.warning(f"Could not fetch models from Ollama: {e}")
        return [llmName]

QA_TEMPLATE = """You are a helpful assistant. You are given a context and a question.
The context contains relevant information. Extract and synthesize an answer from it.
Do NOT use any external knowledge. Do NOT make up information not present in the context.

Context:
{context}

Question: {question}

Answer:"""

QA_PROMPT = PromptTemplate(
    template=QA_TEMPLATE,
    input_variables=["context", "question"]
)

NO_CONTEXT_ANSWER = "I don't have enough information in my knowledge base to answer that question."

def init_llm(vectorstore, model_name=None):
    if model_name is None:
        model_name = llmName
    llm = OllamaLLM(model=model_name, base_url=llmUrl, think=False)
    retriever = ConfidenceRetriever(
        vectorstore=vectorstore,
        similarity_threshold=0.65,
        k=5
    )
    return llm, retriever

SOURCE_META = {
    "local":       ("🖥️", "Local",      "source-local"),
    "sharepoint":  ("☁️", "SharePoint", "source-sharepoint"),
}

def _fetch_answer(question):
    t0 = time.perf_counter()

    raw_results = st.session_state.retriever.vectorstore.similarity_search_with_score(question, k=5)
    st.session_state.debug_scores = [(round(score, 4), doc.page_content[:60]) for doc, score in raw_results]

    docs = st.session_state.retriever._get_relevant_documents(question)
    retrieval_time = st.session_state.retriever.last_retrieval_time

    sources = {
        (doc.metadata["source"], doc.metadata.get("filepath", ""))
        for doc in docs if doc.metadata.get("source")
    }

    if not docs:
        answer = NO_CONTEXT_ANSWER
        llm_time = 0.0
    else:
        context = "\n\n".join(doc.page_content for doc in docs)
        prompt = QA_PROMPT.format(context=context, question=question)
        answer = st.session_state.llm.invoke(prompt)
        llm_time = time.perf_counter() - t0 - retrieval_time

    st.session_state.last_timings = {
        "retrieval": retrieval_time,
        "llm": llm_time,
        "total": time.perf_counter() - t0,
    }
    return answer, sources

def _source_badges_html(sources):
    if not sources:
        return ""
    badges = []
    for src, filepath in sorted(sources):
        icon = SOURCE_META.get(src, ("📄", "", "source-local"))[0]
        css  = SOURCE_META.get(src, ("📄", "", f"source-{src}"))[2]
        label = filepath if filepath else src
        badges.append(
            f'<span class="source-badge {css}" title="{filepath}">'
            f'{icon} <span class="source-path">{label}</span></span>'
        )
    return f'<div class="source-badges">{"".join(badges)}</div>'

def showResponses(container):
    regex_pattern = r'<think>[\s\S]*?<\/think>\n\n'
    sources_history = st.session_state.get("sources_history", [])
    with container:
        if not st.session_state.chat_history:
            st.markdown('''
            <div class="empty-state">
                <div class="empty-logo">🤖</div>
                <p class="empty-title">Ready to assist</p>
                <p class="empty-hint">Ask a question about your indexed documents</p>
            </div>
            ''', unsafe_allow_html=True)
        else:
            ai_idx = 0
            for i, message in enumerate(st.session_state.chat_history):
                if i % 2 == 0:
                    st.chat_message("user").write(message.content)
                else:
                    cleaned_content = re.sub(regex_pattern, '', message.content)
                    msg_sources = sources_history[ai_idx] if ai_idx < len(sources_history) else set()
                    with st.chat_message("assistant"):
                        st.write(cleaned_content)
                        if msg_sources:
                            st.markdown(_source_badges_html(msg_sources), unsafe_allow_html=True)
                    ai_idx += 1

def main():
    st.write(css, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("#### ⚙ Configuration")
        available_models = get_available_models()

        if "selected_model" not in st.session_state:
            st.session_state.selected_model = llmName

        new_model = st.selectbox(
            "LLM Model",
            options=available_models,
            index=available_models.index(st.session_state.selected_model) if st.session_state.selected_model in available_models else 0,
            key="model_selector"
        )

        if new_model != st.session_state.selected_model:
            st.session_state.selected_model = new_model
            st.session_state.llm, st.session_state.retriever = init_llm(st.session_state.vectorstore, new_model)
            st.rerun()

    with st.spinner("Initialisation...", show_time=True):
        if "qdrantClient" not in st.session_state:
            qdrantHelper = QdrantHelper()
            st.session_state.qdrantClient = qdrantHelper.client
            st.session_state.qdrantHelper = qdrantHelper

        if "vectorstore" not in st.session_state:
            st.session_state.vectorstore = st.session_state.qdrantHelper.get_vectorstore()
        if "llm" not in st.session_state:
            st.session_state.llm, st.session_state.retriever = init_llm(st.session_state.vectorstore, st.session_state.selected_model)
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = None
        if "sources_history" not in st.session_state:
            st.session_state.sources_history = []

    model_label = st.session_state.get("selected_model", llmName) or llmName
    st.markdown(f'''
    <div class="rag-header">
        <div class="rag-logo">🤖</div>
        <div>
            <div class="rag-title">Knowledge Base</div>
            <div class="rag-model">LOCAL RAG &middot; <span>{model_label}</span></div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    messages_container = st.container(height=700)
    showResponses(messages_container)

    if prompt := st.chat_input("Ask a question about your documents…"):
        if st.session_state.chat_history is None:
            st.session_state.chat_history = []

        st.session_state.chat_history.append(HumanMessage(content=prompt))

        with messages_container:
            st.chat_message("user").write(prompt)
            with st.chat_message("assistant"):
                with st.spinner(""):
                    answer, sources = _fetch_answer(prompt)

        st.session_state.chat_history.append(AIMessage(content=answer))
        st.session_state.sources_history.append(sources)
        st.rerun()

    if "last_timings" in st.session_state:
        t = st.session_state.last_timings
        st.markdown(f'''
        <div class="timing-row">
            <span class="timing-seg">
                <span class="timing-dot">●</span>
                <span class="timing-label">retrieval</span>
                <span class="timing-val">{t["retrieval"]:.2f}s</span>
            </span>
            <span class="timing-seg">
                <span class="timing-dot">●</span>
                <span class="timing-label">llm</span>
                <span class="timing-val">{t["llm"]:.2f}s</span>
            </span>
            <span class="timing-seg">
                <span class="timing-dot">●</span>
                <span class="timing-label">total</span>
                <span class="timing-val">{t["total"]:.2f}s</span>
            </span>
        </div>
        ''', unsafe_allow_html=True)

    if "debug_scores" in st.session_state:
        with st.expander("🔍 Debug scores"):
            for score, snippet in st.session_state.debug_scores:
                st.caption(f"score={score} | {snippet}...")

if __name__ == '__main__':
    main()
