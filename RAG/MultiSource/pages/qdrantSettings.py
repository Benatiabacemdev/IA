import streamlit as st

col1, col2 = st.columns([1, 3])

st.set_page_config(page_title="VectoreStore", page_icon=":database:")

if "qdrantClient" in st.session_state:
    collections = st.session_state.qdrantClient.get_collections()
    #st.subheader(f"Collection name: {collection.name}")
    st.metric("Number of collections", value=len(collections.collections))
    
    with col1:
        collectionNames = st.radio(
            "Selectionner la collection",
            [
                collection.name for collection in collections.collections
            ],
            index=None,
            key="collectionName",
        )
    with col2:
        if "collectionName" in st.session_state and st.session_state.collectionName != None:
            st.button("Delete collection", key="deleteCollection")
            collection = st.session_state.qdrantClient.get_collection(st.session_state.collectionName)
            st.write(collection)
            st.write(st.session_state.qdrantClient.query_points(st.session_state.collectionName).points)
            if st.session_state.get("deleteCollection", False):
                st.session_state.qdrantClient.delete_collection(st.session_state.collectionName)
                del st.session_state.collectionName
                st.rerun()
else:
    st.write("No Qdrant client configured yet.")