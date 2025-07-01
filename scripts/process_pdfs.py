import os
import json
from pathlib import Path
from PyPDF2 import PdfReader
import re

BASE_DIR = os.path.dirname(__file__)
SOURCE_DIR = os.path.join(BASE_DIR, "..", "data", "data_sources", "articles")
OUTPUT_DIR = os.path.join(BASE_DIR, "..", "data", "json_output", "articles")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "clean_chunks.jsonl")

def extract_text_from_pdf(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        return "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
    except Exception as e:
        print(f"❌ Error reading {pdf_path}: {e}")
        return ""

def clean_text(text):
    text = text.replace('\u200c', ' ')
    text = re.sub(r'[^\S\r\n]{2,}', ' ', text)
    text = re.sub(r'\n{2,}', '\n', text)
    text = re.sub(r'[^\x00-\x7F\u0600-\u06FF\s\n]', '', text)
    return text.strip()

def chunk_text(text, max_words=250):
    words = re.split(r'(\s+)', text)
    chunks, chunk, count = [], [], 0
    for w in words:
        chunk.append(w)
        if w.strip():
            count += 1
        if count >= max_words:
            chunks.append(''.join(chunk).strip())
            chunk, count = [], 0
    if chunk:
        chunks.append(''.join(chunk).strip())
    return chunks

def process_all_pdfs():
    all_chunks = []
    pdf_files = list(Path(SOURCE_DIR).rglob("*.pdf"))
    print(f"🔍 Found {len(pdf_files)} PDF files")

    for pdf_path in pdf_files:
        print(f"📄 Processing: {pdf_path.name}")
        raw_text = extract_text_from_pdf(str(pdf_path))
        if not raw_text:
            continue
        cleaned = clean_text(raw_text)
        chunks = chunk_text(cleaned)
        for chunk in chunks:
            if len(chunk.split()) < 50:
                continue
            all_chunks.append({"source": pdf_path.name, "chunk": chunk})

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"💾 Saving {len(all_chunks)} chunks to {OUTPUT_PATH}")
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        for item in all_chunks:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    process_all_pdfs()
