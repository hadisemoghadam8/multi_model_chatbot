# main.py

import sys
sys.path.append('/home/hadise/chatbot_env')  # افزودن مسیر محیط مجازی به sys.path

import gc
import time
import threading
import pygame
import subprocess
import webbrowser
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# ابزارها و توابع کمکی
from chatbot.chatbot_core import TherapyChatbot
from utils.printer import (
    print_system, print_error, print_success, print_warning, set_language,
    print_bot_panel, print_command_item,
    print_model_switch, print_model_header, print_success_switch_message,
    print_section_header
)
from scripts.pdf_reader import extract_text_from_pdf
import arabic_reshaper
from bidi.algorithm import get_display

# --- تنظیمات اولیه ---
console = Console()
pygame.init()
CLICK_SOUND_PATH = "/home/hadise/chatbot_env/click-234708.mp3"

# --- پیام‌ها به دو زبان ---
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


# --- تعیین زبان بر اساس مدل فعال ---
def get_language(model_name):
    return "en" if model_name == "zephyr" else "fa"

# --- پخش صدای کلیک ---
def play_click():
    try:
        sound = pygame.mixer.Sound(CLICK_SOUND_PATH)
        sound.play()
    except Exception as e:
        print_error(f"مشکل در پخش صدای کلیک: {e}")

# --- نمایش انیمیشن تغییر مدل ---
def animated_switch_message(lang):
    m = messages[lang]
    with console.status(f"[bold green]{m['switching']} 🔄...", spinner="earth"):
        threading.Thread(target=play_click, daemon=True).start()
        time.sleep(2.5)

# --- چاپ پیام کاربر با پنل رنگی ---
def print_user_message(msg):
    panel = Panel.fit(
        Text("[👤 You]: ", style="bold green") + Text(msg, style="white"),
        border_style="green",
        title="You",
        title_align="left"
    )
    console.print(panel)

# --- چاپ لیست دستورات ---
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
        print_command_item(emoji, cmd, desc, color)

# --- نمایش مدل‌ها ---
def show_models(model_names, active_model):
    for idx, model in enumerate(model_names, 1):
        print_model_switch(idx, model, model == active_model)




# --- تابع اصلی برنامه ---
def main():
    model_paths = {
        "zephyr": "/home/hadise/chatbot_env/models/zephyr-7b-beta.Q4_K_M.gguf",
        "dorna": "/home/hadise/chatbot_env/models/dorna-llama3-8b-instruct.Q4_K_M.gguf"
    }
    model_names = list(model_paths.keys())

    chatbot = TherapyChatbot(
        model_paths=model_paths,
        faiss_index_path_fa="/home/hadise/chatbot_env/data/retriever/faiss_index_fa.bin",
        faiss_meta_path_fa="/home/hadise/chatbot_env/data/retriever/faiss_meta_fa.json",
        embed_model="all-MiniLM-L6-v2",
        n_ctx=2048,
        n_gpu_layers=50,
        n_threads=6
    )

    pdf_text = ""
    lang = get_language(chatbot.active_model)
    set_language(lang)
    m = messages[lang]

    print_system(m["welcome"])
    print_model_header(chatbot.active_model, m["active_model"])
    print_system(f"[bold yellow]{m['commands']}[/bold yellow]")
    print_commands_rich(lang)

    while True:
        try:
            lang = get_language(chatbot.active_model)
            set_language(lang)
            m = messages[lang]

            user_input = input(f"\n{m['ask'].format(chatbot.active_model)} ").strip()

            if not user_input:
                print_error(m["invalid_input"])
                continue

            if user_input.lower() in ("/exit", "exit", "خروج"):
                print_system(m["bye"])
                break

            elif user_input.lower() in ("/loadpdf", "load pdf"):
                Tk().withdraw()
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

                if new_input.isdigit():
                    idx = int(new_input) - 1
                    if 0 <= idx < len(model_names):
                        next_model = model_names[idx]
                    else:
                        print_error(m["invalid_input"])
                        continue
                elif new_input in model_names:
                    next_model = new_input
                else:
                    print_error(m["invalid_input"])
                    continue

                if next_model == chatbot.active_model:
                    print_warning("⚠️ همین مدل فعال است!")
                    continue

                animated_switch_message(lang)

                try:
                    if hasattr(chatbot, "llm") and chatbot.llm:
                        del chatbot.llm
                        chatbot.llm = None
                        gc.collect()
                        print_success("✅ مدل قبلی آزاد شد!")
                except Exception as e:
                    print_error(f"❌ مشکل در آزادسازی مدل قبلی: {e}")

                chatbot.switch_model(next_model)
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
                # فقط متن ساده کاربر را به متد ask بده
                answer = chatbot.ask(user_input)
                print_bot_panel(answer)

        except KeyboardInterrupt:
            print_system("\n" + m["bye"])
            break
        except Exception as e:
            print_error(f"{m['error']} {e}")

# --- اجرای برنامه ---
if __name__ == "__main__":
        # اجرای رابط گرافیکی Streamlit
    subprocess.Popen(["streamlit", "run", "chat_ui/app.py"])
    time.sleep(2)
    webbrowser.open("http://localhost:8501")
    
    main()
    pygame.quit()
