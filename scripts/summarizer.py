#summarizer.py
from typing import List
# import textwrap
from chatbot.chatbot_core import TherapyChatbot
import os
import gc

# تنظیم مسیرها برای مدل‌ها و ایندکس‌ها
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
MODEL_PATHS = {
    "zephyr": os.path.join(BASE_DIR, "models", "zephyr-7b-beta.Q4_K_M.gguf"),
    "dorna": os.path.join(BASE_DIR, "models", "dorna-llama3-8b-instruct.Q4_K_M.gguf")
}

# ابزار چانک‌سازی متن
def chunk_text(text: str, max_tokens: int = 300) -> List[str]:
    words = text.split()
    chunks = []
    for i in range(0, len(words), max_tokens):
        chunk = " ".join(words[i:i+max_tokens])
        chunks.append(chunk)
    return chunks

# ابزار خلاصه‌سازی چانک‌ها
def summarize_chunks(chunks: List[str], model, max_summary_tokens=100) -> str:
    summaries = []
    for chunk in chunks:
        summary = model.ask(f"لطفاً این متن را خلاصه کن:\n\n{chunk}\n\nخلاصه:")
        summaries.append(summary.strip())
    return "\n".join(summaries)

# تابع اصلی برای استفاده در Streamlit
def summarize(text: str, model_name: str = "dorna") -> str:
    model_path = MODEL_PATHS.get(model_name)
    if not model_path:
        raise ValueError(f"مدل '{model_name}' پیدا نشد.")

    # ایجاد یک نمونه موقتی از چت‌بات فقط برای خلاصه‌سازی
    chatbot = TherapyChatbot(
        model_paths={model_name: model_path},
        faiss_index_path_fa=None,
        faiss_meta_path_fa=None,
        n_ctx=1024,
        n_threads=4
    )
    chatbot.switch_model(model_name)

    # چانک‌سازی و خلاصه‌سازی
    chunks = chunk_text(text)
    summary = summarize_chunks(chunks, chatbot)
    gc.collect()
    return summary
