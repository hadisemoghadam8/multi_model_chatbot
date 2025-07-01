#views/chatbot.py
import os
from chatbot.chatbot_core import TherapyChatbot
import streamlit as st

# --- Base directories for locating model and data files ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "..", "models")
DATA_DIR = os.path.join(BASE_DIR, "..", "data", "retriever")

# --- Paths to available GGUF models ---
model_paths = {
    "dorna": os.path.join(MODEL_DIR, "dorna-llama3-8b-instruct.Q4_K_M.gguf"),
    "zephyr": os.path.join(MODEL_DIR, "zephyr-7b-beta.Q4_K_M.gguf")
}

# --- Multilingual text labels used in UI (Persian and English) ---
texts = {
    "fa": {
        "title": "چت‌بات درمانی",
        "input_placeholder": "پیام خود را اینجا بنویسید...",
        "loading": "در حال تولید پاسخ...",
        "error_response": "در پردازش پیام مشکلی پیش آمد.",
        "select_model": "مدل گفتگو را انتخاب کن / Choose model",
        "select_model_help": "ترجیح می‌دی با زفیر صحبت کنی یا درنا؟",
        "model_loading": "در حال بارگذاری مدل «{}»...",
        "model_loaded": "مدل «{}» با موفقیت بارگذاری شد.",
        "model_load_error": "خطا در بارگذاری مدل «{}»: {}",
        "model_not_loaded": "مدل «{}» هنوز بارگذاری نشده است.",
        "free_model_error": "خطا در آزادسازی مدل قبلی: {}"
    },
    "en": {
        "title": "Therapy Chatbot",
        "input_placeholder": "Write your message here...",
        "loading": "Generating response...",
        "error_response": "There was a problem processing your message.",
        "select_model": "Select conversation model / انتخاب مدل گفتگو",
        "select_model_help": "Would you prefer to talk to Zephyr or Dorna?",
        "model_loading": "Loading model '{}'",
        "model_loaded": "Model '{}' loaded successfully.",
        "model_load_error": "Error loading model '{}': {}",
        "model_not_loaded": "Model '{}' has not been loaded yet.",
        "free_model_error": "Error freeing previous model: {}"
    }
}


# --- Initialize session state variables if not set ---
if "selected_model" not in st.session_state:
    st.session_state.selected_model = "dorna"

if "models" not in st.session_state:
    st.session_state.models = {}

# --- Temporary language used for displaying the model select box ---
tmp_language = "fa" if st.session_state.selected_model == "dorna" else "en"
tmp_txt = texts[tmp_language]

# --- UI for selecting a model ---
selected_model = st.selectbox(
    label=tmp_txt["select_model"],
    options=list(model_paths.keys()),
    index=list(model_paths.keys()).index(st.session_state.selected_model),
    help=tmp_txt["select_model_help"],
    key="model_selector"
)

# --- Final language based on selected model ---
language = "fa" if selected_model == "dorna" else "en"
txt = texts[language]

# --- Page setup: title and icon ---
st.set_page_config(page_title="Therapy Chatbot", page_icon="💬")
st.title(txt["title"])

# --- Load or initialize chat message history for the selected model ---
msg_key = f"messages_{selected_model}"
if msg_key not in st.session_state:
    st.session_state[msg_key] = []

# --- If the user switched models, unload the previous one ---
if selected_model != st.session_state.selected_model:
    old_model = st.session_state.selected_model
    if old_model in st.session_state.models:
        try:
            del st.session_state.models[old_model]
            import gc
            gc.collect() # Explicitly free up GPU/CPU memory
        except Exception as e:
            st.warning(txt["free_model_error"].format(e))
    st.session_state.selected_model = selected_model

# --- Load messages for current model session ---
messages = st.session_state[msg_key]

# --- Load the selected model if not already loaded ---
if selected_model not in st.session_state.models:
    with st.spinner(txt["model_loading"].format(selected_model)):
        try:
            st.session_state.models[selected_model] = TherapyChatbot(
                model_paths={selected_model: model_paths[selected_model]},
                faiss_index_path_fa=os.path.join(DATA_DIR, "faiss_index_fa.bin"),
                faiss_meta_path_fa=os.path.join(DATA_DIR, "faiss_meta_fa.json"),
                n_ctx=4096,
                n_gpu_layers=28,
                n_threads=6
            )
            st.success(txt["model_loaded"].format(selected_model))
        except Exception as e:
            st.error(txt["model_load_error"].format(selected_model, e))
            st.stop()

# --- Retrieve the active chatbot instance ---
chatbot = st.session_state.models.get(selected_model)
if chatbot is None:
    st.error(txt["model_not_loaded"].format(selected_model))
    st.stop()

# --- Display chat history messages ---
for message in messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Handle new user input ---
if prompt := st.chat_input(txt["input_placeholder"]):
        # Append user message
    messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
        # Generate assistant reply
    with st.chat_message("assistant"):
        with st.spinner(txt["loading"]):
            try:
                chatbot.language = language
                response = chatbot.ask(
                    question=prompt,
                    max_tokens=512,
                    temperature=0.3
                )
                st.markdown(response)
            except Exception as e:
                st.error(f"❌ {txt['error_response']}")
                response = txt["error_response"]


            # Append assistant message
    messages.append({"role": "assistant", "content": response})
