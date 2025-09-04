import streamlit as st

home = st.Page(
    "pages/home.py", title="Home", icon=":material/dashboard:", default=True
)
qdrant = st.Page("pages/qdrantSettings.py", title="Vector Store", icon=":material/database:")
#admin = st.Page("pages/admins.py", title="Administration", icon=":material/settings:")
sync = st.Page("pages/synchronisation.py", title="Synchronisation", icon=":material/directory_sync:")

pg = st.navigation(
        {
            "Home": [home],
            "Settings": [qdrant,sync]
        }
    )
pg.run()