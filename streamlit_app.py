# streamlit_app.py
import streamlit as st

# --- PAGE SETUP ---
about_page = st.Page(
    "views/about_me.py",
    title="About Me",
    icon=":material/account_circle:",
    default=True,
)

project_2_page = st.Page(
    "views/chatbot.py",
    title="Chat Bot",
    icon=":material/smart_toy:",
)

# --- NAVIGATION SETUP [WITH SECTIONS]---
pg = st.navigation(
    {
        "Info": [about_page],
        "Projects": [project_2_page],  # فقط Chat Bot اینجا مونده
    }
)

# --- RUN NAVIGATION ---
pg.run()
