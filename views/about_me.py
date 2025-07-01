import streamlit as st

# --- Contact Form Section ---
@st.experimental_dialog("Contact Me")
def show_contact_form():
    st.markdown("**📧 Email:** hadisemoghadam8@gmail.com")
    st.markdown("**🔗 GitHub:** [hadisemoghadam8](https://github.com/hadisemoghadam8 )")


# --- Introduction ---
st.title("Hadiseh Moghadam", anchor=False)
st.write("💡 Working in the field of Artificial Intelligence, focusing on NLP and building intelligent Farsi chatbots using local LLMs.")

if st.button("✉️ Contact Me"):
    show_contact_form()


# --- Experience & Projects ---
st.write("\n")
st.subheader("Experience & Projects", anchor=False)
st.write(
    """
    - Developed a **bilingual (Farsi-English) therapeutic chatbot** using local LLMs such as **Zephyr 7B** and **Dorna-LLaMA3**, powered by **llama.cpp** for offline execution.
    - Implemented a full **RAG (Retrieval-Augmented Generation)** pipeline using **FAISS** and **sentence-transformers** for Persian content retrieval and contextual Q&A.
    - Integrated a **PDF reader** using **PyMuPDF** to enable document-based interaction and context injection.
    - Designed a **ChatGPT-style UI** with **Streamlit multipage navigation**, including model switching, language selection, and session history management.
    - Deployed **quantized GGUF models** on local GPU (RTX 3050 Ti) with optimized memory usage and performance settings.
    """
)

# --- Technical Skills ---
st.write("\n")
st.subheader("Technical Skills", anchor=False)
st.write(
    """
    - **Programming**: Python (Transformers, FAISS, PyMuPDF, Streamlit, sentence-transformers), Bash
    - **Language Models**: Zephyr 7B, Dorna-LLaMA3, Mistral (GGUF format), llama.cpp
    - **NLP Tools**: Prompt Engineering, FAISS, RAG, PDF Processing, Language Detection
    - **Tools & Frameworks**: Git, HuggingFace, CUDA 12.8, Streamlit, FAISS indexing
    """
)