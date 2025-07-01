# streamlit_app.py


import streamlit as st

# --- PAGE SETUP ---

# Define the "About Me" page (default landing page)
about_page = st.Page(
    "views/about_me.py",                # Path to the About Me page file
    title="About Me",                   # Title shown in the sidebar
    icon=":material/account_circle:",  # Material icon
    default=True                        # Set this as the default page
)

# Define the "Chat Bot" project page
project_2_page = st.Page(
    "views/chatbot.py",                # Path to the chatbot page file
    title="Chat Bot",                  # Title shown in the sidebar
    icon=":material/smart_toy:"        # Material icon
)

# --- NAVIGATION SETUP [WITH SECTIONS] ---

# Organize pages into categories: Info and Projects
pg = st.navigation(
    {
        "Info": [about_page],          # Personal info section
        "Projects": [project_2_page],  # Project section (currently only Chatbot)
    }
)

# --- RUN NAVIGATION ---
# Render the selected page based on user interaction
pg.run()
