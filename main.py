# main.py

# Add the project environment path to Python's module search path
import sys
sys.path.append('/home/hadise/chatbot_env')

# Standard libraries for memory management, timing, threading, and system interaction
import gc             # For manual garbage collection
import time           # For sleep delays, timestamps
import threading      # For running tasks concurrently (e.g. sound playing)
import pygame         # For playing audio (click sounds)
import subprocess     # For launching external processes (like Streamlit)
import webbrowser     # For opening URLs in a browser

# GUI file picker (for selecting PDF files)
from tkinter import Tk
from tkinter.filedialog import askopenfilename

# Rich library for colorful terminal UI
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Project modules: Chatbot core logic
from chatbot.chatbot_core import TherapyChatbot

# Utility functions for printing messages with formatting
from utils.printer import (
    print_system, print_error, print_success, print_warning, set_language,
    print_bot_panel, print_command_item,
    print_model_switch, print_model_header, print_success_switch_message,
    print_section_header
)

# Function to extract text from PDF files
from scripts.pdf_reader import extract_text_from_pdf

# Arabic text reshaping and bidi support (for properly displaying Persian/Arabic)
import arabic_reshaper
from bidi.algorithm import get_display

# --- Initial Setup ---

console = Console()              # Rich console for pretty terminal output
pygame.init()                    # Initialize Pygame (used for audio playback)
CLICK_SOUND_PATH = "/home/hadise/chatbot_env/click-234708.mp3"  # Path to click sound

# --- Multilingual Interface Messages (Farsi & English) ---

messages = {
    "fa": {
        "welcome": "به چت‌بات درمانگر خوش آمدید!",
        "active_model": "مدل فعال",
        "commands": "دستورات",
        "loadpdf": "/loadpdf یا load pdf — بارگذاری فایل PDF",
        "switch": "/switch یا switch — تغییر مدل زبانی",
        "reset": "/reset یا reset — پاکسازی تاریخچه چت",
        "models": "/models یا models — لیست مدل‌های موجود",
        "exit": "/exit یا exit — خروج از برنامه",
        "ask": "({}) پیام یا دستور وارد کنید:",
        "bye": "خداحافظ! 🌸",
        "file_loaded": "📄 فایل PDF بارگذاری شد!",
        "file_empty": "⚠️ فایل خالی بود!",
        "no_file": "⚠️ فایلی انتخاب نشد.",
        "switching": "در حال تغییر مدل",
        "switch_success": "مدل با موفقیت تغییر کرد به",
        "invalid_input": "⚠️ ورودی نامعتبر است!",
        "error": "❌ خطا:",
        "switch_prompt": "🔄 شماره یا نام مدل جدید را وارد کنید:",
        "reset_success": "چت پاک شد! 🧹"
    },
    "en": {
        "welcome": "Welcome to the Therapist Chatbot!",
        "active_model": "Active Model",
        "commands": "Commands",
        "loadpdf": "/loadpdf or load pdf — Load a PDF file",
        "switch": "/switch or switch — Switch language model",
        "reset": "/reset or reset — Clear chat history",
        "models": "/models or models — List available models",
        "exit": "/exit or exit — Exit the program",
        "ask": "({}) Enter your message or a command:",
        "bye": "Goodbye! 👋",
        "file_loaded": "📄 PDF file loaded!",
        "file_empty": "⚠️ PDF file is empty!",
        "no_file": "⚠️ No file selected.",
        "switching": "Switching model",
        "switch_success": "Model switched successfully to",
        "invalid_input": "⚠️ Invalid input!",
        "error": "❌ Error:",
        "switch_prompt": "Enter the number or name of the new model:",
        "reset_success": "Chat history cleared! 🧹"
    }
}


# --- Determine the language based on the active model name ---
def get_language(model_name):
    # If the active model is "zephyr", use English; otherwise, use Persian
    return "en" if model_name == "zephyr" else "fa"


# --- Play click sound using pygame ---
def play_click():
    try:
        sound = pygame.mixer.Sound(CLICK_SOUND_PATH)  # Load the sound file
        sound.play()  # Play it
    except Exception as e:
        print_error(f"Failed to play click sound: {e}")  # Show error if any


# --- Show a loading animation with sound when switching models ---
def animated_switch_message(lang):
    m = messages[lang]  # Get language-specific messages
    with console.status(f"[bold green]{m['switching']} 🔄...", spinner="earth"):
        # Play click sound in a background thread
        threading.Thread(target=play_click, daemon=True).start()
        # Wait for animation to complete
        time.sleep(2.5)

# --- Display user's input message inside a styled panel ---
def print_user_message(msg):
    panel = Panel.fit(
        Text("[👤 You]: ", style="bold green") + Text(msg, style="white"),
        border_style="green",
        title="You",
        title_align="left"
    )
    console.print(panel)  # Print the message in a green panel


# --- Print available commands in colorful rows based on the selected language ---
def print_commands_rich(lang):
    cmds = {
        "fa": [
            ("📄", "/loadpdf", "بارگذاری فایل PDF", "yellow"),
            ("🔄", "/switch", "تغییر مدل زبانی", "cyan"),
            ("🧹", "/reset", "پاک‌سازی تاریخچه گفتگو", "magenta"),
            ("🧠", "/models", "مشاهده مدل‌های موجود", "green"),
            ("🚪", "/exit", "خروج از برنامه", "red"),
        ],
        "en": [
            ("📄", "/loadpdf", "Load a PDF file", "yellow"),
            ("🔄", "/switch", "Switch language model", "cyan"),
            ("🧹", "/reset", "Clear chat history", "magenta"),
            ("🧠", "/models", "List available models", "green"),
            ("🚪", "/exit", "Exit the program", "red"),
        ]
    }

    for emoji, cmd, desc, color in cmds[lang]:
        print_command_item(emoji, cmd, desc, color)  # Print each command line


# --- Display a list of available models with indicators for the active one ---
def show_models(model_names, active_model):
    for idx, model in enumerate(model_names, 1):
        print_model_switch(idx, model, model == active_model)


# --- Main function that runs the terminal chatbot ---
def main():
    # Dictionary of model names and their corresponding GGUF file paths
    model_paths = {
        "zephyr": "/home/hadise/chatbot_env/models/zephyr-7b-beta.Q4_K_M.gguf",
        "dorna": "/home/hadise/chatbot_env/models/dorna-llama3-8b-instruct.Q4_K_M.gguf"
    }
    model_names = list(model_paths.keys())  # Extract model names list

    # Initialize the therapy chatbot with paths and configuration
    chatbot = TherapyChatbot(
        model_paths=model_paths,
        faiss_index_path_fa="/home/hadise/chatbot_env/data/retriever/faiss_index_fa.bin",
        faiss_meta_path_fa="/home/hadise/chatbot_env/data/retriever/faiss_meta_fa.json",
        embed_model="all-MiniLM-L6-v2",  # Embedding model for FAISS
        n_ctx=2048,                      # Context length
        n_gpu_layers=50,                # Number of GPU layers to offload
        n_threads=6                     # Number of threads to use
    )

    pdf_text = ""  # Placeholder for extracted PDF text

    # Detect language based on the active model and set it
    lang = get_language(chatbot.active_model)
    set_language(lang)
    m = messages[lang]  # Load message dictionary for current language

    # Show welcome messages and initial status
    print_system(m["welcome"])
    print_model_header(chatbot.active_model, m["active_model"])
    print_system(f"[bold yellow]{m['commands']}[/bold yellow]")  # Print "Commands" section title
    print_commands_rich(lang)  # Display all supported commands


    while True:
        try:
            # Refresh language settings in case the active model changed
            lang = get_language(chatbot.active_model)
            set_language(lang)
            m = messages[lang]

            # Ask user for input (message or command)
            user_input = input(f"\n{m['ask'].format(chatbot.active_model)} ").strip()

            # Handle empty input
            if not user_input:
                print_error(m["invalid_input"])
                continue

            # --- Exit command ---
            if user_input.lower() in ("/exit", "exit", "خروج"):
                print_system(m["bye"])
                break


            elif user_input.lower() in ("/loadpdf", "load pdf"):
                Tk().withdraw()  # Hide the main Tkinter window
                path = askopenfilename(
                    title="انتخاب فایل PDF" if lang == "fa" else "Select a PDF File",
                    filetypes=[("PDF Files", "*.pdf")]
                )
                if path:
                    pdf_text = extract_text_from_pdf(path)
                    if pdf_text.strip():
                        print_system(m["file_loaded"])
                    else:
                        print_error(m["file_empty"])
                else:
                    print_error(m["no_file"])
            elif user_input.lower() in ("/switch", "switch"):
                print_system(m["models"])
                show_models(model_names, chatbot.active_model)
                new_input = input(f"\n{m['switch_prompt']} ").strip()

                if not new_input:
                    print_error(m["invalid_input"])
                    continue

                # Allow user to select model by number
                if new_input.isdigit():
                    idx = int(new_input) - 1
                    if 0 <= idx < len(model_names):
                        next_model = model_names[idx]
                    else:
                        print_error(m["invalid_input"])
                        continue
                # Or by model name directly
                elif new_input in model_names:
                    next_model = new_input
                else:
                    print_error(m["invalid_input"])
                    continue

                # If selected model is already active, show warning
                if next_model == chatbot.active_model:
                    print_warning("⚠️ This model is already active!")
                    continue

                # Show loading animation and play click sound
                animated_switch_message(lang)

                try:
                    # Free up resources used by the current model
                    if hasattr(chatbot, "llm") and chatbot.llm:
                        del chatbot.llm
                        chatbot.llm = None
                        gc.collect()
                        print_success("✅ Previous model unloaded!")
                except Exception as e:
                    print_error(f"❌ Error unloading previous model: {e}")

                # Switch to the new model
                chatbot.switch_model(next_model)

                # Update language settings after switching
                lang = get_language(chatbot.active_model)
                set_language(lang)
                m = messages[lang]

                print_success_switch_message(m["switch_success"], chatbot.active_model)
                print_section_header(m["commands"])
                print_commands_rich(lang)

            elif user_input.lower() in ("/reset", "reset"):
                chatbot.reset_history()
                print_system(m["reset_success"])

            elif user_input.lower() in ("/models", "models"):
                print_system(m["models"])
                show_models(model_names, chatbot.active_model)

            else:
                # Pass normal user input to the chatbot for response
                answer = chatbot.ask(user_input)
                print_bot_panel(answer)

        except KeyboardInterrupt:
            print_system("\n" + m["bye"])
            break
        except Exception as e:
            print_error(f"{m['error']} {e}")


# --- Program Entry Point ---
if __name__ == "__main__":
    # Launch the Streamlit UI in the background
    subprocess.Popen(["streamlit", "run", "chat_ui/app.py"])
    time.sleep(2)  # Wait for Streamlit to initialize

    # Open the app in the browser
    webbrowser.open("http://localhost:8501")

    # Start the chatbot main loop
    main()

    # Cleanup pygame resources on exit
    pygame.quit()
