# chunk_books.py
import os
import fitz  # PyMuPDF
import json
from tqdm import tqdm

def extract_text_chunks(pdf_path, lang, chunk_size=500):
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    doc.close()

    words = full_text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk_words = words[i:i+chunk_size]
        chunk_text = " ".join(chunk_words)
        chunks.append({
            "text": chunk_text,
            "lang": lang,
            "source": pdf_path,
            "chunk_id": i // chunk_size
        })
    return chunks

def main():
    input_dirs = {
        "fa": "data_sources/books/fa",
        "en": "data_sources/books/en"
    }
    os.makedirs("processed_chunks", exist_ok=True)
    output_path = "processed_chunks/chunks.jsonl"

    all_chunks = []
    for lang, folder in input_dirs.items():
        for filename in tqdm(os.listdir(folder), desc=f"Processing {lang}"):
            if filename.endswith(".pdf"):
                pdf_path = os.path.join(folder, filename)
                try:
                    chunks = extract_text_chunks(pdf_path, lang)
                    all_chunks.extend(chunks)
                except Exception as e:
                    print(f"[ERROR] Failed on {filename}: {e}")

    with open(output_path, "w", encoding="utf-8") as f:
        for chunk in all_chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")

    print(f"✅ Done! {len(all_chunks)} chunks saved to {output_path}")

if __name__ == "__main__":
    main()
