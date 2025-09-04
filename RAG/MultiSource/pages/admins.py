import streamlit as st

from helpers.ragHelper import RAGHelper
from helpers.qdrantHelper import QdrantHelper

ragHelper = RAGHelper()
qdHelper = QdrantHelper()

st.set_page_config(page_title="Administration", page_icon=":settings:")
st.subheader("Your documents")

pdf_docs = st.file_uploader("Upload your PDFs here and click on 'Process'", accept_multiple_files=True)

if st.button("Process"):
    with st.spinner("Processing"):
        # get pdf text
        raw_text = ragHelper.get_pdf_text(pdf_docs)

        # get the text chunks
        text_chunks = ragHelper.get_text_chunks(raw_text)

        qdHelper.add_ToVectorStore(text_chunks, st.session_state.vectorstore)