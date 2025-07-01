# chatbot/chatbot_core.py


import json
import faiss
import numpy as np
from llama_cpp import Llama
from sentence_transformers import SentenceTransformer
import sys
import os
from langdetect import detect
from utils.printer import print_success, print_system

# --- Add current directory to Python path ---
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# --- RTL (right-to-left) Persian text reshaping ---
import arabic_reshaper
from bidi.algorithm import get_display
import torch.cuda as cuda

def estimate_max_gpu_layers(model_size: str, vram_gb: float) -> int:
    """
    Estimate the maximum number of GPU layers based on model size and available VRAM.
    
    Parameters:
        model_size (str): Model size (e.g., "7B", "8B")
        vram_gb (float): Available VRAM in GB

    Returns:
        int: Recommended n_gpu_layers value
    """
    # Estimated memory consumption per layer in GB (Q4_K_M quantization)
    MEMORY_PER_LAYER_GB = {
        "7B": 0.16,   # ~160MB per layer for 7B models
        "8B": 0.18,   # ~180MB per layer for 8B models
    }

    if model_size not in MEMORY_PER_LAYER_GB:
        raise ValueError(f"Unsupported model size: {model_size}. Use '7B' or '8B'.")

    layer_memory = MEMORY_PER_LAYER_GB[model_size]
    max_layers = int(vram_gb * 1024 / (layer_memory * 1024))  # convert GB to MB

    # Limit to a reasonable range
    return min(max(max_layers, 0), 32)

class TherapyChatbot:
    def __init__(self, model_paths: dict, faiss_index_path_fa: str, faiss_meta_path_fa: str,
                embed_model: str = "all-MiniLM-L6-v2", n_ctx: int = 4096,
                n_gpu_layers: int = 28, n_threads: int = 6):
        """Initialize the Therapist Chatbot with multiple LLaMA models and retriever."""
        self.model_paths = model_paths
        self.active_model = list(model_paths.keys())[0]
        self.language = "en"  # Default language is English
        self.n_ctx = n_ctx
        self.n_gpu_layers = n_gpu_layers
        self.n_threads = n_threads
        self.model = self.load_model(self.model_paths[self.active_model])
        self.embedder = SentenceTransformer(embed_model)

            # Load FAISS index and metadata for Persian
        self.index_fa = faiss.read_index(faiss_index_path_fa)
        with open(faiss_meta_path_fa, encoding="utf-8") as f:
            self.meta_fa = json.load(f)

        # --- Attempt to load the English version of FAISS index and metadata, if available ---
        # Replace "_fa." in file names with "_en." to get the expected English paths
        faiss_index_path_en = faiss_index_path_fa.replace("_fa.", "_en.")
        faiss_meta_path_en = faiss_meta_path_fa.replace("_fa.", "_en.")

        # Check if both English index and metadata files exist
        if os.path.exists(faiss_index_path_en) and os.path.exists(faiss_meta_path_en):
                # Load the English FAISS index
            self.index_en = faiss.read_index(faiss_index_path_en)
                # Load the associated metadata (list of chunks)
            with open(faiss_meta_path_en, encoding="utf-8") as f:
                self.meta_en = json.load(f)
        else:
                # If files are not found, fall back to empty values
            self.index_en = None
            self.meta_en = []
        self.history = []

    def load_model(self, model_path: str):
        """Load a LLaMA model from disk with specified runtime configuration."""
        return Llama(
            model_path=model_path,
            n_ctx=self.n_ctx,                  # Number of context tokens
            n_gpu_layers=self.n_gpu_layers,    # Number of layers offloaded to GPU
            n_threads=self.n_threads,          # Number of CPU threads to use
            use_mlock=True,                    # Prevent the model from being swapped out of RAM
            verbose=False                      # Suppress detailed logs
        )

    def detect_model_size(model_path: str) -> str:
        """
        Detect model size from its filename.
        Example: dorna-llama3-8b-instruct.Q4_K_M.gguf → returns "8B"
        """
        filename = os.path.basename(model_path).lower()
        if "7b" in filename:
            return "7B"
        elif "8b" in filename:
            return "8B"
        else:
            raise ValueError("Model size not found in filename (expected 7B or 8B)")
        
    def switch_model(self, new_model_name: str):
        """Switch to a different model by name and reset conversation history."""
        
        # Check if the requested model exists in the model paths
        if new_model_name not in self.model_paths:
            raise ValueError(f"Model '{new_model_name}' not found.")

        # Remove the current model from memory
        del self.model

        # Load the new model
        self.active_model = new_model_name
        self.model = self.load_model(self.model_paths[self.active_model])

        # Set chatbot language based on model
        if new_model_name == "dorna":
            self.language = "fa"  # Persian
        else:
            self.language = "en"  # English

        # Clear the current chat history
        self.reset_history()

        # Display success messages in both Persian and English
        if os.environ.get("TERM_UI", "1") == "1":
            print_success(f"مدل با موفقیت تغییر کرد به {self.active_model}")
            print_system(f"✨ Model {self.active_model} is ready.")



    def retrieve_chunks(self, question: str, top_k: int = 5, lang: str = None):
        """Retrieve top-k relevant text chunks from the FAISS index based on question embedding."""
        lang = self.language if lang is None else lang
        try:
            # Generate sentence embedding for the question
            q_emb = self.embedder.encode([question], convert_to_numpy=True).astype('float32')

            # Choose the appropriate index and metadata based on language
            index = self.index_fa if lang == "fa" else self.index_en
            metadata = self.meta_fa if lang == "fa" else self.meta_en

            # If the index or metadata is missing, return empty list
            if index is None or not metadata:
                return []

            # Search the index for most relevant entries
            D, I = index.search(np.array(q_emb), top_k)
            chunks = []
            for idx in I[0]:
                if 0 <= idx < len(metadata):
                    chunk = metadata[idx]
                    chunks.append({
                        "content": chunk.get("content", ""),
                        "chunk_id": chunk.get("chunk_id"),
                        "source": chunk.get("source", "")
                    })
            return chunks
        except Exception as e:
            print(f"Error retrieving data from FAISS: {e}")
            return []

    def detect_question_complexity(self, question: str) -> int:
        """Determine number of chunks to retrieve based on question complexity."""
        length = len(question.split())
        if length < 8:
            return 3
        elif length < 20:
            return 5
        else:
            return 7

    def build_system_prompt(self, retrieved_chunks):
        """Construct the initial system prompt with context from retrieved chunks."""
        
        # Set the base instruction prompt depending on language
        if self.language == "fa":
            system_prompt = (
                "تو یک درمانگر حرفه‌ای شناختی-رفتاری فارسی زبان هستی. "
                "باید با زبان کاملا فارسی، ساده و علمی پاسخ بدهی. "
                "پاسخ‌ها باید کوتاه، خاص و کاربردی باشند."
            )
        else:
            system_prompt = (
                "You are a professional Cognitive-Behavioral Therapist. "
                "Respond in clear, simple, and scientific English. "
                "Provide brief and focused answers."
            )

        # Add reference context from the retrieved documents
        if retrieved_chunks:
            context_text = "\nReference information:\n"
            for chunk in retrieved_chunks:
                if chunk["content"]:
                    context_text += f"- {chunk['content'].strip()}\n"
        else:
            context_text = "\n(No sources found; please answer based on general knowledge.)"

        return system_prompt + context_text


    def sanitize_question(self, question: str) -> str:
        """Ensure the question is in the correct language."""
        if self.language == "fa" and not any('\u0600' <= c <= '\u06FF' for c in question):
            return "لطفا سوال خود را به زبان فارسی بنویسید."
        elif self.language == "en" and any('\u0600' <= c <= '\u06FF' for c in question):
            return "Please write your question in English."
        return question

    def ask(self, question: str, max_tokens: int = 512, temperature: float = 0.3) -> str:
        """
        Generate a response to the user's question using the active model.
        Supports both Zephyr (English) and Dorna (Persian) models with optional RAG.
        """
        llm = self.model

        # Automatically detect question's language
        question_language = self.detect_language(question)

        # If the active model is Zephyr (English chat, prompt-style input)
        if self.active_model == "zephyr":
            system_prompt = (
                "You are a professional cognitive-behavioral therapist. "
                "Respond briefly and directly to the user's problems. "
                "Avoid long stories or explanations. Focus on practical advice and support."
            )
            # Build a single-prompt message
            prompt = system_prompt + "\nUser: " + question.strip() + "\nTherapist:"

            # Call the model (Zephyr works in prompt-style completion)
            response = llm(
                prompt=prompt,
                max_tokens=150,
                temperature=0.3,
                top_p=0.7,
                repeat_penalty=1.1,
                stop=["User:", "Therapist:"]
            )

            # Extract and clean the generated text
            raw_text = response["choices"][0]["text"]
            safe_text = raw_text.encode("utf-8", errors="replace").decode("utf-8").strip()
            return safe_text

        # For Dorna or other models supporting chat-style input
        if question_language == 'fa':
            # Persian input
            sanitized_question = self.sanitize_question(question)
            self.history.append({"role": "user", "content": sanitized_question})

            # Retrieve relevant chunks based on question complexity (RAG)
            top_k = self.detect_question_complexity(sanitized_question)
            retrieved_chunks = self.retrieve_chunks(sanitized_question, top_k=top_k, lang=question_language)
            system_prompt = self.build_system_prompt(retrieved_chunks)

            # Construct chat history with system prompt
            messages = [{"role": "system", "content": system_prompt}]
            messages += self.history[-6:]  # Limit to last 6 turns
            messages.append({"role": "user", "content": sanitized_question})

            # Generate chat completion
            response = llm.create_chat_completion(
                messages=messages,
                max_tokens=150,
                temperature=0.25,
                top_p=0.7,
                repeat_penalty=1.1,
                stop=["مراجع:", "درمانگر:"]
            )

            raw = response["choices"][0]["message"]["content"]
            answer = raw.encode("utf-8", errors="replace").decode("utf-8").strip()

        else:
            # English input (chat-style models like Dorna or fallback Zephyr)
            sanitized_question = self.sanitize_question(question)
            self.history.append({"role": "user", "content": sanitized_question})

            # Retrieve English context if available
            top_k = self.detect_question_complexity(sanitized_question)
            retrieved_chunks = self.retrieve_chunks(sanitized_question, top_k=top_k, lang=question_language)
            system_prompt = self.build_system_prompt(retrieved_chunks)

            messages = [{"role": "system", "content": system_prompt}]
            messages += self.history[-6:]
            messages.append({"role": "user", "content": sanitized_question})

            response = llm.create_chat_completion(
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=0.9,
                repeat_penalty=1.1,
                stop=["Client:", "Therapist:"]
            )

            raw = response["choices"][0]["message"]["content"]
            answer = raw.encode("utf-8", errors="replace").decode("utf-8").strip()

        # Save model response to history
        self.history.append({"role": "assistant", "content": answer})

        # Return the final response
        return answer

    def detect_language(self, question: str) -> str:
        """Detect the language of the question."""
        try:
            return detect(question)  # 'en' or 'fa'
        except:
            return "unknown"

    def print_model_switch_menu(self):
        """Print a terminal menu for switching between available models."""
        active_model = self.active_model
        models = list(self.model_paths.keys())
        print(f"Current active model: [bold green]{active_model}[/bold green]")
        print("\nSelect a new model:")
        for model in models:
            marker = "[bold green]✅[/bold green]" if model == active_model else "[bold yellow]➤[/bold yellow]"
            print(f"{marker} {model}")
        print("\nTo change the model, please enter the new model's number or name.")

    def reset_history(self):
        """Clear the conversation history."""
        self.history = []
        print("🧹 Chat history has been cleared!")


    def fix_rtl(self, text: str) -> str:
        """Display Persian text correctly in terminal with reshaper and bidi."""
        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped)
