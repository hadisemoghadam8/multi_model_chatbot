# config.py

MODEL_PATHS = {
    "zephyr": "models/zephyr-7b-beta.Q4_K_M.gguf",
    "dorna": "models/dorna-llama3-8b-instruct.Q4_K_M.gguf"
}

# مسیر فایل‌های faiss
FAISS_INDEX_FA = "retriever/faiss_index_fa.bin"
FAISS_META_FA = "retriever/faiss_meta_fa.json"
