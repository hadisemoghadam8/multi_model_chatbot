# summarizer.py

from typing import List
# import textwrap  # Not used currently
from chatbot.chatbot_core import TherapyChatbot
import os
import gc  # For memory cleanup

# Set project base directory
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Paths to local models
MODEL_PATHS = {
    "zephyr": os.path.join(BASE_DIR, "models", "zephyr-7b-beta.Q4_K_M.gguf"),
    "dorna": os.path.join(BASE_DIR, "models", "dorna-llama3-8b-instruct.Q4_K_M.gguf")
}

# Function to split large text into chunks (by word count)
def chunk_text(text: str, max_tokens: int = 300) -> List[str]:
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), max_tokens):
        chunk = " ".join(words[i:i+max_tokens])
        chunks.append(chunk)
    
    return chunks

# Function to summarize text chunks one by one
def summarize_chunks(chunks: List[str], model, max_summary_tokens=100) -> str:
    summaries = []
    
    for chunk in chunks:
        # Ask the model to summarize each chunk
        summary = model.ask(f"لطفاً این متن را خلاصه کن:\n\n{chunk}\n\nخلاصه:")
        summaries.append(summary.strip())
    
    return "\n".join(summaries)

# Main function to summarize text, designed for Streamlit or external use
def summarize(text: str, model_name: str = "dorna") -> str:
    model_path = MODEL_PATHS.get(model_name)
    
    if not model_path:
        raise ValueError(f"Model '{model_name}' not found.")
    
    # Create a temporary chatbot instance for summarization
    chatbot = TherapyChatbot(
        model_paths={model_name: model_path},
        faiss_index_path_fa=None,  # No retriever needed for summarization
        faiss_meta_path_fa=None,
        n_ctx=1024,  # Context length
        n_threads=4  # Number of CPU threads
    )
    
    chatbot.switch_model(model_name)  # Activate the selected model

    # Chunk the text and summarize each part
    chunks = chunk_text(text)
    summary = summarize_chunks(chunks, chatbot)

    gc.collect()  # Clean up memory

    return summary
