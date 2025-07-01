#views/chatbot.py
import os
from chatbot.chatbot_core import TherapyChatbot
import streamlit as st

# --- تنظیمات اولیه ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "..", "models")
DATA_DIR = os.path.join(BASE_DIR, "..", "data", "retriever")

# --- مسیر مدل‌ها ---
model_paths = {
    "dorna": os.path.join(MODEL_DIR, "dorna-llama3-8b-instruct.Q4_K_M.gguf"),
    "zephyr": os.path.join(MODEL_DIR, "zephyr-7b-beta.Q4_K_M.gguf")
}

# --- متون چندزبانه ---
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


# --- مقداردهی اولیه session_state ---
if "selected_model" not in st.session_state:
    st.session_state.selected_model = "dorna"

if "models" not in st.session_state:
    st.session_state.models = {}

# --- تعیین زبان و متون اولیه برای selectbox ---
tmp_language = "fa" if st.session_state.selected_model == "dorna" else "en"
tmp_txt = texts[tmp_language]

# --- انتخاب مدل توسط کاربر ---
selected_model = st.selectbox(
    label=tmp_txt["select_model"],
    options=list(model_paths.keys()),
    index=list(model_paths.keys()).index(st.session_state.selected_model),
    help=tmp_txt["select_model_help"],
    key="model_selector"
)

# --- تعیین زبان نهایی ---
language = "fa" if selected_model == "dorna" else "en"
txt = texts[language]

# --- تنظیمات صفحه ---
st.set_page_config(page_title="Therapy Chatbot", page_icon="💬")
st.title(txt["title"])

# --- کلید پیام‌ها ---
msg_key = f"messages_{selected_model}"
if msg_key not in st.session_state:
    st.session_state[msg_key] = []

# --- سوییچ مدل ---
if selected_model != st.session_state.selected_model:
    old_model = st.session_state.selected_model
    if old_model in st.session_state.models:
        try:
            del st.session_state.models[old_model]
            import gc
            gc.collect()
        except Exception as e:
            st.warning(txt["free_model_error"].format(e))
    st.session_state.selected_model = selected_model

# --- بارگذاری پیام‌های قبلی ---
messages = st.session_state[msg_key]

# --- بارگذاری مدل در صورت نیاز ---
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

# --- بازیابی مدل ---
chatbot = st.session_state.models.get(selected_model)
if chatbot is None:
    st.error(txt["model_not_loaded"].format(selected_model))
    st.stop()

# --- نمایش تاریخچه گفتگو ---
for message in messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- دریافت پیام جدید از کاربر ---
if prompt := st.chat_input(txt["input_placeholder"]):
    messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

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

    messages.append({"role": "assistant", "content": response})
