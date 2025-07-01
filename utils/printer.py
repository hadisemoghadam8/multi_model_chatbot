from rich.console import Console
from rich.panel import Panel
from rich.text import Text
import arabic_reshaper
from bidi.algorithm import get_display


console = Console()

# وضعیت زبان فعلی
current_lang = "en"

def set_language(lang):
    global current_lang
    current_lang = lang

def print_system(message):
    prefix = "⚙️ System: " if current_lang == "en" else "⚙️ سیستم: "
    console.print(f"{prefix}{message}")

def print_error(message):
    prefix = "❌ Error: " if current_lang == "en" else "❌ خطا: "
    console.print(f"{prefix}{message}")

def print_success(message):
    prefix = "✅ Success: " if current_lang == "en" else "✅ موفقیت: "
    console.print(f"{prefix}{message}")

def print_warning(message):
    prefix = "⚠️ Warning: " if current_lang == "en" else "⚠️ هشدار: "
    console.print(f"{prefix}{message}")

def print_bot_panel(answer):
    if current_lang == "fa":
        reshaped = arabic_reshaper.reshape(answer)
        answer = get_display(reshaped)
        prefix = "[🤖 بات]: "
        title = "بات"
    else:
        prefix = "[🤖 Bot]: "
        title = "Bot"

    panel = Panel.fit(
        Text(prefix, style="bold blue") + Text(answer, style="white"),
        border_style="cyan",
        title=title,
        title_align="left"
    )
    console.print(panel)


def print_user_panel(message):
    if current_lang == "fa":
        reshaped = arabic_reshaper.reshape(message)
        message = get_display(reshaped)
        prefix = "[👤 شما]: "
        title = "شما"
    else:
        prefix = "[👤 You]: "
        title = "You"

    panel = Panel.fit(
        Text(prefix, style="bold green") + Text(message, style="white"),
        border_style="green",
        title=title,
        title_align="left"
    )
    console.print(panel)


def print_command_item(emoji, cmd, desc, color):
    console.print(f"{emoji} [bold {color}]{cmd}[/bold {color}] — {desc}")

def print_model_switch(idx, model, is_active):
    marker = "✅" if is_active else ""
    console.print(f"[bold cyan]{idx}.[/bold cyan] {model} {marker}")

def print_model_header(model_name, label):
    console.print(f"{label}: [bold cyan]{model_name}[/bold cyan]")

def print_success_switch_message(message, model_name):
    console.print(f"✨ [green]{message} [bold cyan]{model_name}[/bold cyan] ✨[/green]")

def print_section_header(title):
    console.print(f"\n[bold yellow]{title}[/bold yellow]")
