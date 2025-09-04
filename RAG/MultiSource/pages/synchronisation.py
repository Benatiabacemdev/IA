import streamlit as st
import os
import datetime
import pandas as pd
from helpers.postgresHelper import PostgresHelper
from helpers.qdrantHelper import QdrantHelper
from helpers.ragHelper import RAGHelper
from helpers.sharepointHelper import SharePointHelper
from models.document import DocumentModel

st.set_page_config(layout="wide")
st.set_page_config(page_title="Synchronisation", page_icon=":directory_sync:")

css = '''
<style>
    .stTabs .st-cr{ gap: 2rem;}
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
    font-size:2rem;
    }
</style>
'''
st.markdown(css, unsafe_allow_html=True)

def select_folder():
    import tkinter as tk
    from tkinter import filedialog
    root = tk.Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory()
    root.destroy()
    return folder_path

def compare_datetimes(dt1, dt2):
    """Compare deux datetime, naïve ou aware, en UTC."""
    if dt1.tzinfo is None:
        dt1 = dt1.replace(tzinfo=datetime.timezone.utc)
    if dt2.tzinfo is None:
        dt2 = dt2.replace(tzinfo=datetime.timezone.utc)
    return dt1.replace(microsecond=0) == dt2.replace(microsecond=0)

def add_document(dbHelper, document: DocumentModel, raw_text):
    text_chunks = ragHelper.get_text_chunks(raw_text)
    uids = qdrantHelper.add_ToVectorStore(text_chunks, st.session_state.vectorstore)
    document.uids = ",".join([str(uid) for uid in uids])
    dbHelper.insert_document(document)

def sync_local_documents():
    selected_folder_path = st.session_state.get("folderPath", None)
    st.write("Select the folder containing your PDF documents to synchronize with the vector store and database.")
    col1, col2 = st.columns([1,6])
    with col1:
        folder_select_button = st.button("Select Folder")
    if folder_select_button:
        selected_folder_path = select_folder()
    with col2:
        if selected_folder_path:
            st.session_state.folderPath = selected_folder_path
            st.write("Selected folder path:", selected_folder_path)
    if selected_folder_path:
        sync_documents_button = st.button("Syncronize documents")
        if sync_documents_button:
            with st.spinner("Synchronizing documents..."):
                dbHelper = PostgresHelper()
                table_placeholder = st.empty()
                st.session_state.syncDataFrame = pd.DataFrame(columns=["File Name", "Last Modified", "Created", "Size (ko)", "Status"])
                for root, dirs, files in os.walk(selected_folder_path):
                    for fileName in files:
                        if fileName.lower().endswith('.pdf'):
                            fileFullPath = os.path.join(root, fileName)
                            modifiedStamp = datetime.datetime.fromtimestamp(os.path.getmtime(fileFullPath))
                            createdStamp = datetime.datetime.fromtimestamp(os.path.getctime(fileFullPath))
                            size = os.path.getsize(fileFullPath) / 1000
                            new_row = pd.DataFrame([[fileName, modifiedStamp, createdStamp, size, "Pending"]], columns=st.session_state.syncDataFrame.columns)
                            st.session_state.syncDataFrame = pd.concat([st.session_state.syncDataFrame, new_row], ignore_index=True)
                            table_placeholder.dataframe(st.session_state.syncDataFrame)
                            documentExist = dbHelper.get_document(fileName, fileFullPath)
                            status = "Synchronized: new"
                            if documentExist is not None:
                                if (compare_datetimes(documentExist.modifieddate, modifiedStamp)
                                    and compare_datetimes(documentExist.createddate, createdStamp)
                                    and float(documentExist.size) == float(size)):
                                    status = "Already synchronized"
                                    st.session_state.syncDataFrame.at[len(st.session_state.syncDataFrame)-1, "Status"] = status
                                    table_placeholder.dataframe(st.session_state.syncDataFrame)
                                    continue
                                else:
                                    deletedPoints = qdrantHelper.delete_points(documentExist.uids.split(","))
                                    if deletedPoints:
                                        deletedDocument = dbHelper.delete_document(documentExist.id)
                                        if deletedDocument:
                                            status = "Synchronized: updated"
                            newDocument = DocumentModel(
                                id=None,
                                filename=fileName,
                                filepath=fileFullPath,
                                modifieddate=modifiedStamp,
                                createddate=createdStamp,
                                size=size,
                                uids=None)
                            raw_text = ragHelper.get_pdf_text(fileFullPath)
                            add_document(dbHelper, newDocument, raw_text)
                            st.session_state.syncDataFrame.at[len(st.session_state.syncDataFrame)-1, "Status"] = status
                            table_placeholder.dataframe(st.session_state.syncDataFrame)
                dbHelper.close()
                st.success("Documents synchronized successfully!")

def sync_sharepoint_documents():
    sync_documents_button = st.button("Syncronize documents")
    if sync_documents_button:
        with st.spinner("Synchronizing documents..."):
            spHelper = SharePointHelper()
            files = spHelper.get_library_files("Documents")
            dbHelper = PostgresHelper()
            table_placeholder = st.empty()
            st.session_state.syncDataFrame = pd.DataFrame(columns=["File Name", "Last Modified", "Created", "Size (ko)", "Status"])
            for file in files:
                fileName = file["name"]
                if fileName.lower().endswith('.pdf'):
                    fileFullPath = file["webUrl"]
                    modifiedDate = datetime.datetime.fromisoformat(file["lastModifiedDateTime"].replace("Z", "+00:00"))
                    createdDate = datetime.datetime.fromisoformat(file["createdDateTime"].replace("Z", "+00:00"))
                    size = file["size"] / 1000
                    new_row = pd.DataFrame([[fileName, modifiedDate, createdDate, size, "Pending"]], columns=st.session_state.syncDataFrame.columns)
                    st.session_state.syncDataFrame = pd.concat([st.session_state.syncDataFrame, new_row], ignore_index=True)
                    table_placeholder.dataframe(st.session_state.syncDataFrame)
                    documentExist = dbHelper.get_document(fileName, fileFullPath)
                    status = "Synchronized: new"
                    if documentExist is not None:
                        if (compare_datetimes(documentExist.modifieddate, modifiedDate)
                            and compare_datetimes(documentExist.createddate, createdDate)
                            and float(documentExist.size) == float(size)):
                            status = "Already synchronized"
                            st.session_state.syncDataFrame.at[len(st.session_state.syncDataFrame)-1, "Status"] = status
                            table_placeholder.dataframe(st.session_state.syncDataFrame)
                            continue
                        else:
                            deletedPoints = qdrantHelper.delete_points(documentExist.uids.split(","))
                            if deletedPoints:
                                deletedDocument = dbHelper.delete_document(documentExist.id)
                                if deletedDocument:
                                    status = "Synchronized: updated"
                    newDocument = DocumentModel(
                        id=None,
                        filename=fileName,
                        filepath=fileFullPath,
                        modifieddate=modifiedDate,
                        createddate=createdDate,
                        size=size,
                        uids=None)
                    content = spHelper.get_pdf_text(file["driveId"], file["id"])
                    add_document(dbHelper, newDocument, content)
                    st.session_state.syncDataFrame.at[len(st.session_state.syncDataFrame)-1, "Status"] = status
                    table_placeholder.dataframe(st.session_state.syncDataFrame)
            dbHelper.close()
            st.success("Documents synchronized successfully!")


ragHelper = RAGHelper()
qdrantHelper = QdrantHelper()

tab1, tab2 = st.tabs(["Local", "SharePoint"])
with tab1:
    st.header("Local folder synchronization")
    sync_local_documents()
with tab2:
    st.header("SharePoint synchronization")
    sync_sharepoint_documents()



